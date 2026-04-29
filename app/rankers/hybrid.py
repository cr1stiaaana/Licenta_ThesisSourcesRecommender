"""Hybrid Ranker — fuses semantic and keyword retrieval results using RRF or weighted sum."""

from __future__ import annotations

import hashlib
import unicodedata
from typing import Any

from app.config import AppConfig
from app.models import (
    ArticleRecommendation,
    RetrievalResult,
    WebResourceRecommendation,
    WebRetrievalResult,
)

# RRF constant (from the original RRF paper)
_RRF_K = 60


def _normalize_title(title: str) -> str:
    """Lowercase, strip, and normalize unicode for deduplication."""
    normalized = unicodedata.normalize("NFKD", title)
    return normalized.lower().strip()


def _dedup_key(doi: str | None, title: str) -> str:
    """Return a canonical deduplication key: lowercased DOI if present, else normalized title."""
    if doi:
        return doi.lower().strip()
    return _normalize_title(title)


def _url_item_id(url: str) -> str:
    """Return SHA-256 hex digest of the URL for use as item_id."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


class HybridRanker:
    """Merges and re-ranks results from semantic and keyword retrievers.

    Args:
        config: Application configuration.
        feedback_store: Optional FeedbackStore instance (Any to avoid circular imports).
    """

    def __init__(self, config: AppConfig, feedback_store: Any = None) -> None:
        self._config = config
        self._feedback_store = feedback_store

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def fuse_articles(
        self,
        semantic: RetrievalResult,
        keyword: RetrievalResult,
        top_k: int,
        semantic_weight: float,
        keyword_weight: float,
    ) -> list[ArticleRecommendation]:
        """Merge and deduplicate article results from two retrievers.

        Uses Reciprocal Rank Fusion (default) or weighted score sum depending on
        ``AppConfig.fusion_strategy``.  Applies feedback signal boost when enabled,
        then filters by ``min_article_score`` and returns the top-k results ordered
        by descending score.

        Args:
            semantic: Results from the semantic retriever.
            keyword: Results from the keyword retriever.
            top_k: Maximum number of results to return.
            semantic_weight: Weight applied to the semantic retriever's contribution.
            keyword_weight: Weight applied to the keyword retriever's contribution.

        Returns:
            List of :class:`ArticleRecommendation` ordered by descending score.
        """
        config = self._config

        # ── Step 1: build per-retriever rank maps ────────────────────────────
        # Map dedup_key → (ScoredArticle, 1-based rank)
        semantic_map: dict[str, tuple[Any, int]] = {}
        for rank, sa in enumerate(semantic.items, start=1):
            key = _dedup_key(sa.article.doi, sa.article.title)
            if key not in semantic_map:
                semantic_map[key] = (sa, rank)

        keyword_map: dict[str, tuple[Any, int]] = {}
        for rank, sa in enumerate(keyword.items, start=1):
            key = _dedup_key(sa.article.doi, sa.article.title)
            if key not in keyword_map:
                keyword_map[key] = (sa, rank)

        # ── Step 2: collect all unique candidates ────────────────────────────
        all_keys = set(semantic_map) | set(keyword_map)

        # ── Step 3: compute fusion score ─────────────────────────────────────
        scored: list[tuple[str, float, Any]] = []  # (key, score, ScoredArticle)

        for key in all_keys:
            sem_entry = semantic_map.get(key)
            kw_entry = keyword_map.get(key)

            # Prefer the ScoredArticle from whichever retriever has it
            sa = (sem_entry or kw_entry)[0]  # type: ignore[index]

            if config.fusion_strategy == "weighted_sum":
                score = self._weighted_sum_score(
                    sem_entry, kw_entry, semantic_weight, keyword_weight
                )
            else:
                # Default: RRF
                score = self._rrf_score(
                    sem_entry, kw_entry, semantic_weight, keyword_weight
                )

            scored.append((key, score, sa))

        # ── Step 4: apply feedback signal boost ──────────────────────────────
        if config.feedback_signal_enabled and self._feedback_store is not None:
            scored = self._apply_feedback_boost(scored)

        # ── Step 5: filter by min_article_score ──────────────────────────────
        scored = [(k, s, sa) for k, s, sa in scored if s >= config.min_article_score]

        # ── Step 6: sort descending and take top-k ───────────────────────────
        scored.sort(key=lambda x: x[1], reverse=True)
        scored = scored[:top_k]

        # ── Step 7: build ArticleRecommendation objects ───────────────────────
        recommendations: list[ArticleRecommendation] = []
        for _key, score, sa in scored:
            article = sa.article
            abstract_snippet = ""
            if article.abstract:
                abstract_snippet = article.abstract[:300]

            rec = ArticleRecommendation(
                resource_type="article",
                title=article.title,
                authors=list(article.authors),
                year=article.year,
                abstract_snippet=abstract_snippet,
                score=score,
                doi=article.doi,
                url=article.url,
                quality_warning=None,
                item_id=article.id,
            )
            recommendations.append(rec)

        return recommendations

    def rank_web_resources(
        self,
        web: WebRetrievalResult,
        top_k: int,
    ) -> list[WebResourceRecommendation]:
        """Filter and rank web resources by descending web_score.

        Applies ``min_web_score`` threshold and returns at most ``top_k`` results.

        Args:
            web: Raw web retrieval results.
            top_k: Maximum number of results to return.

        Returns:
            List of :class:`WebResourceRecommendation` ordered by descending web_score.
        """
        config = self._config

        filtered = [
            item for item in web.items if item.web_score >= config.min_web_score
        ]
        filtered.sort(key=lambda x: x.web_score, reverse=True)
        filtered = filtered[:top_k]

        recommendations: list[WebResourceRecommendation] = []
        for item in filtered:
            rec = WebResourceRecommendation(
                resource_type="web",
                title=item.title,
                url=item.url,
                snippet=item.snippet,
                web_score=item.web_score,
                keywords=list(item.keywords),
                quality_warning=None,
                item_id=_url_item_id(item.url),
            )
            recommendations.append(rec)

        return recommendations

    # ──────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _rrf_score(
        sem_entry: tuple[Any, int] | None,
        kw_entry: tuple[Any, int] | None,
        semantic_weight: float,
        keyword_weight: float,
    ) -> float:
        """Compute Reciprocal Rank Fusion score.

        ``RRF_score(d) = Σ_r  weight_r / (k + rank_r(d))``
        where k = 60.
        """
        score = 0.0
        if sem_entry is not None:
            _, rank = sem_entry
            score += semantic_weight / (_RRF_K + rank)
        if kw_entry is not None:
            _, rank = kw_entry
            score += keyword_weight / (_RRF_K + rank)
        return score

    @staticmethod
    def _weighted_sum_score(
        sem_entry: tuple[Any, int] | None,
        kw_entry: tuple[Any, int] | None,
        semantic_weight: float,
        keyword_weight: float,
    ) -> float:
        """Compute weighted sum of raw retrieval scores."""
        score = 0.0
        if sem_entry is not None:
            sa, _ = sem_entry
            score += semantic_weight * sa.score
        if kw_entry is not None:
            sa, _ = kw_entry
            score += keyword_weight * sa.score
        return score

    def _apply_feedback_boost(
        self,
        scored: list[tuple[str, float, Any]],
    ) -> list[tuple[str, float, Any]]:
        """Apply feedback signal boost to candidates with high average ratings.

        For each candidate, queries the FeedbackStore for its aggregate average
        rating.  If ``avg_rating >= feedback_signal_min_rating``, applies:

            boosted = rrf_score + boost * (avg_rating - 1) / 4

        Items with no ratings are left unchanged.
        """
        config = self._config
        boosted: list[tuple[str, float, Any]] = []

        for key, score, sa in scored:
            item_id = sa.article.id
            try:
                result = self._feedback_store.get_ratings(item_id, session_id=None)
                avg_rating = result.average_rating
                if (
                    avg_rating is not None
                    and avg_rating >= config.feedback_signal_min_rating
                ):
                    normalized = (avg_rating - 1) / 4  # maps [1,5] → [0,1]
                    score = score + config.feedback_signal_boost * normalized
            except Exception:
                # If the feedback store is unavailable, skip boost for this item
                pass

            boosted.append((key, score, sa))

        return boosted
