"""KeywordRetriever: BM25-based keyword search over the article corpus."""

from __future__ import annotations

import os
import pickle
import re
from pathlib import Path

from app.article_store import ArticleStore
from app.config import AppConfig
from app.models import Query, RetrievalResult, ScoredArticle


class KeywordRetrieverError(Exception):
    """Raised when the keyword retriever encounters an index failure."""


class KeywordRetriever:
    """Retrieves articles using BM25 keyword matching.

    The BM25 index is built from the article corpus at construction time.
    If a persisted index exists at ``config.bm25_index_path``, it is loaded
    from disk; otherwise the index is built from scratch and saved.
    """

    def __init__(self, article_store: ArticleStore, config: AppConfig) -> None:
        self._article_store = article_store
        self._config = config
        self._bm25 = self._load_or_build_index()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_or_build_index(self):  # type: ignore[return]
        """Load the BM25 index from disk or build and persist it.

        Returns:
            A ``rank_bm25.BM25Okapi`` instance.

        Raises:
            KeywordRetrieverError: if loading or building the index fails.
        """
        try:
            from rank_bm25 import BM25Okapi  # type: ignore
        except ImportError as exc:
            raise KeywordRetrieverError(
                f"rank_bm25 is not installed: {exc}"
            ) from exc

        index_path = self._config.bm25_index_path

        if os.path.exists(index_path):
            try:
                with open(index_path, "rb") as fh:
                    return pickle.load(fh)
            except Exception as exc:
                raise KeywordRetrieverError(
                    f"Failed to load BM25 index from '{index_path}': {exc}"
                ) from exc

        # Build from corpus
        try:
            corpus = self._article_store.get_all_texts()
            bm25 = BM25Okapi(corpus)
        except Exception as exc:
            raise KeywordRetrieverError(
                f"Failed to build BM25 index: {exc}"
            ) from exc

        # Persist to disk
        try:
            Path(index_path).parent.mkdir(parents=True, exist_ok=True)
            with open(index_path, "wb") as fh:
                pickle.dump(bm25, fh)
        except Exception as exc:
            raise KeywordRetrieverError(
                f"Failed to save BM25 index to '{index_path}': {exc}"
            ) from exc

        return bm25

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Tokenize *text* by splitting on whitespace and punctuation.

        Tokens are lowercased and empty strings are filtered out.
        """
        tokens = re.split(r"[\s\W]+", text.lower())
        return [t for t in tokens if t]

    # ── Public API ────────────────────────────────────────────────────────────

    def retrieve(self, query: Query, top_k: int) -> RetrievalResult:
        """Return the top-*k* articles ranked by BM25 score.

        BM25 scores are normalized by dividing by the maximum score so that
        all returned scores are in ``[0.0, 1.0]``.  When no terms match (all
        scores are zero), an empty :class:`~app.models.RetrievalResult` is
        returned without raising an error.

        Args:
            query:  The user query; ``query.combined_text()`` is tokenized.
            top_k:  Maximum number of results to return.

        Returns:
            A :class:`~app.models.RetrievalResult` with ``source="keyword"``.

        Raises:
            KeywordRetrieverError: if the BM25 index is unavailable or scoring
                fails unexpectedly.
        """
        tokens = self._tokenize(query.combined_text())

        try:
            scores = self._bm25.get_scores(tokens)
        except Exception as exc:
            raise KeywordRetrieverError(f"BM25 scoring failed: {exc}") from exc

        max_score = float(scores.max()) if len(scores) > 0 else 0.0

        # When no terms match, return an empty result (not an error)
        if max_score == 0.0:
            return RetrievalResult(items=[], source="keyword")

        # Normalize scores to [0.0, 1.0]
        normalized_scores = scores / max_score

        # Rank by score descending and take top_k
        import numpy as np  # already a transitive dep via faiss/numpy

        top_indices = np.argsort(normalized_scores)[::-1][:top_k]

        articles = self._article_store.get_all_articles_ordered()

        items: list[ScoredArticle] = []
        for idx in top_indices:
            idx_int = int(idx)
            if idx_int >= len(articles):
                continue
            score = float(normalized_scores[idx_int])
            if score <= 0.0:
                break  # remaining scores are zero
            items.append(ScoredArticle(article=articles[idx_int], score=score))

        return RetrievalResult(items=items, source="keyword")
