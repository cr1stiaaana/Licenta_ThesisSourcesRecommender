"""AcademicWebRetriever — live search for academic papers via Semantic Scholar and arXiv APIs.

This retriever fetches academic articles from external APIs at query time (no local corpus needed).
Results are merged with the local ArticleStore results by the HybridRanker.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal

import requests

from app.models import Article, Query, RetrievalResult, ScoredArticle

logger = logging.getLogger(__name__)

_SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"
_ARXIV_API = "http://export.arxiv.org/api/query"


class AcademicWebRetriever:
    """Retrieves academic papers from Semantic Scholar and arXiv APIs in parallel.

    No API key required. Results are scored by relevance (API ranking position).
    """

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    def retrieve(self, query: Query, top_k: int) -> RetrievalResult:
        """Search Semantic Scholar and arXiv in parallel, merge results, return top_k.

        Parameters
        ----------
        query:
            User query (title + abstract + keywords).
        top_k:
            Maximum number of articles to return.

        Returns
        -------
        RetrievalResult
            Merged results from both APIs, scored by rank position.
        """
        search_text = query.combined_text()

        results_by_source: dict[str, list[ScoredArticle]] = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self._search_semantic_scholar, search_text, top_k): "semantic_scholar",
                executor.submit(self._search_arxiv, search_text, top_k): "arxiv",
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    results_by_source[source] = future.result()
                except Exception as exc:
                    logger.warning("AcademicWebRetriever: %s search failed: %s", source, exc)
                    results_by_source[source] = []

        # Merge: Semantic Scholar first, then arXiv
        merged: list[ScoredArticle] = []
        merged.extend(results_by_source.get("semantic_scholar", []))
        merged.extend(results_by_source.get("arxiv", []))

        # Deduplicate by DOI (prefer first occurrence)
        seen_dois: set[str] = set()
        deduped: list[ScoredArticle] = []
        for item in merged:
            doi = item.article.doi
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)
            deduped.append(item)

        # Return top_k
        return RetrievalResult(items=deduped[:top_k], source="academic_web")

    # ── Semantic Scholar ──────────────────────────────────────────────────

    def _search_semantic_scholar(self, query: str, limit: int) -> list[ScoredArticle]:
        """Search Semantic Scholar API and return scored articles."""
        params = {
            "query": query,
            "limit": min(limit, 20),  # Increased from 10 to 20
            "fields": "title,abstract,authors,year,externalIds,url",
        }
        try:
            resp = requests.get(
                _SEMANTIC_SCHOLAR_API,
                params=params,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("Semantic Scholar API error: %s", exc)
            return []

        papers = data.get("data", [])
        results: list[ScoredArticle] = []

        for rank, paper in enumerate(papers):
            title = paper.get("title", "").strip()
            abstract = paper.get("abstract", "").strip()
            if not title:
                continue

            authors_data = paper.get("authors", [])
            authors = [a.get("name", "") for a in authors_data if a.get("name")]

            year = paper.get("year")
            external_ids = paper.get("externalIds") or {}
            doi = external_ids.get("DOI", "").strip()
            arxiv_id = external_ids.get("ArXiv", "").strip()
            url = paper.get("url", "").strip()

            # Generate a stable ID
            if doi:
                article_id = f"doi:{doi}"
            elif arxiv_id:
                article_id = f"arxiv:{arxiv_id}"
            else:
                article_id = f"s2:{paper.get('paperId', '')}"

            # Score by rank: 1.0 for rank 0, 0.5 for rank 1, etc.
            score = 1.0 / (rank + 1)

            article = Article(
                id=article_id,
                title=title,
                abstract=abstract or None,
                authors=authors or None,
                year=year,
                doi=doi or None,
                url=url or None,
                language="en",  # Semantic Scholar is primarily English
            )

            results.append(ScoredArticle(article=article, score=score))

        return results

    # ── arXiv ─────────────────────────────────────────────────────────────

    def _search_arxiv(self, query: str, limit: int) -> list[ScoredArticle]:
        """Search arXiv API and return scored articles."""
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": min(limit, 10),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        try:
            resp = requests.get(
                _ARXIV_API,
                params=params,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            xml_text = resp.text
        except Exception as exc:
            logger.warning("arXiv API error: %s", exc)
            return []

        # Parse XML (simple extraction without lxml for now)
        results: list[ScoredArticle] = []
        entries = xml_text.split("<entry>")[1:]  # Skip the feed header

        for rank, entry_xml in enumerate(entries[:limit]):
            title = self._extract_xml_tag(entry_xml, "title")
            summary = self._extract_xml_tag(entry_xml, "summary")
            published = self._extract_xml_tag(entry_xml, "published")
            arxiv_id = self._extract_xml_tag(entry_xml, "id")

            if not title:
                continue

            # Extract year from published date (format: 2023-01-15T12:34:56Z)
            year = None
            if published:
                try:
                    year = int(published.split("-")[0])
                except (ValueError, IndexError):
                    pass

            # Extract authors (multiple <author><name>...</name></author>)
            authors = []
            for author_block in entry_xml.split("<author>")[1:]:
                name = self._extract_xml_tag(author_block, "name")
                if name:
                    authors.append(name)

            # arXiv ID from URL (e.g., http://arxiv.org/abs/1706.03762v5)
            arxiv_id_clean = ""
            if arxiv_id and "arxiv.org/abs/" in arxiv_id:
                arxiv_id_clean = arxiv_id.split("/abs/")[-1].split("v")[0]

            article_id = f"arxiv:{arxiv_id_clean}" if arxiv_id_clean else f"arxiv:unknown_{rank}"

            # Score by rank
            score = 1.0 / (rank + 1)

            article = Article(
                id=article_id,
                title=title.strip(),
                abstract=summary.strip() if summary else None,
                authors=authors or None,
                year=year,
                doi=None,
                url=arxiv_id if arxiv_id else None,
                language="en",
            )

            results.append(ScoredArticle(article=article, score=score))

        return results

    @staticmethod
    def _extract_xml_tag(xml: str, tag: str) -> str:
        """Extract the first occurrence of <tag>content</tag> from XML string."""
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start = xml.find(start_tag)
        if start == -1:
            return ""
        start += len(start_tag)
        end = xml.find(end_tag, start)
        if end == -1:
            return ""
        return xml[start:end].strip()
