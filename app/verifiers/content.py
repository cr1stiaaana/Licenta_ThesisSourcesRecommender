"""ContentVerifier: clickbait detection and domain blocklist filtering."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

import numpy as np

from app.config import AppConfig
from app.i18n import t
from app.models import ArticleRecommendation, WebResourceRecommendation

if TYPE_CHECKING:
    from app.retrievers.semantic import SemanticRetriever


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors.

    Returns 0.0 if either vector has zero norm to avoid division by zero.
    """
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* to the range [lo, hi]."""
    return max(lo, min(hi, value))


def _extract_hostname(url: str) -> str:
    """Extract the hostname from a URL, stripping any leading 'www.' prefix."""
    try:
        hostname = urlparse(url).hostname or ""
        # Strip leading 'www.' so that 'www.example.com' → 'example.com'
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname.lower()
    except Exception:
        return ""


def _is_domain_blocked(url: str, blocklist: list[str]) -> bool:
    """Return True if the URL's hostname or any parent domain is in *blocklist*.

    For example, ``"spam.example.com"`` matches blocklist entry ``"example.com"``.
    """
    if not blocklist:
        return False

    hostname = _extract_hostname(url)
    if not hostname:
        return False

    # Normalise blocklist entries (strip leading 'www.' for consistency)
    normalised_blocklist = set()
    for entry in blocklist:
        entry = entry.lower().strip()
        if entry.startswith("www."):
            entry = entry[4:]
        normalised_blocklist.add(entry)

    # Check the hostname itself and each parent domain
    parts = hostname.split(".")
    for i in range(len(parts)):
        candidate = ".".join(parts[i:])
        if candidate in normalised_blocklist:
            return True
    return False


class ContentVerifier:
    """Detects clickbait results and filters blocklisted web domains.

    Uses the same multilingual embedding model as :class:`SemanticRetriever`
    (via its :meth:`~app.retrievers.semantic.SemanticRetriever.encode` method)
    to compute title and content similarity scores without loading a second
    model instance.

    No HTTP requests are made during evaluation.
    """

    def __init__(self, semantic_retriever: "SemanticRetriever") -> None:
        self._retriever = semantic_retriever

    # ── Public API ────────────────────────────────────────────────────────────

    def verify(
        self,
        articles: list[ArticleRecommendation],
        web_resources: list[WebResourceRecommendation],
        query_embedding: np.ndarray,
        query_language: str,
        config: AppConfig,
    ) -> tuple[list[ArticleRecommendation], list[WebResourceRecommendation]]:
        """Filter and flag articles and web resources for content quality.

        Processing rules
        ----------------
        Articles with a non-empty abstract:
            - Compute ``title_sim`` and ``content_sim`` against *query_embedding*.
            - If ``(title_sim - content_sim) > mismatch_threshold``:
                - ``Quality_Score = score * (1 - clamp(title_sim - content_sim, 0, 1))``
                - Set ``quality_warning`` to the localized string.
            - Exclude items whose ``Quality_Score < min_article_score``.

        Articles with no abstract:
            - Retained as-is without a ``quality_warning``.

        Web resources:
            - Check domain against ``domain_blocklist`` first; exclude if matched.
            - Apply the same mismatch check using the snippet.
            - Exclude items whose ``Quality_Score < min_web_score``.

        Args:
            articles:        Ranked article recommendations from the ranker.
            web_resources:   Ranked web resource recommendations from the ranker.
            query_embedding: Pre-computed embedding of the user query.
            query_language:  ``"ro"`` or ``"en"`` — controls warning text.
            config:          Runtime configuration (thresholds, blocklist, etc.).

        Returns:
            A tuple ``(verified_articles, verified_web_resources)``.
        """
        warning_text = t("quality_warning", query_language)

        verified_articles = self._verify_articles(
            articles, query_embedding, warning_text, config
        )
        verified_web = self._verify_web_resources(
            web_resources, query_embedding, warning_text, config
        )
        return verified_articles, verified_web

    # ── Private helpers ───────────────────────────────────────────────────────

    def _verify_articles(
        self,
        articles: list[ArticleRecommendation],
        query_embedding: np.ndarray,
        warning_text: str,
        config: AppConfig,
    ) -> list[ArticleRecommendation]:
        result: list[ArticleRecommendation] = []

        for item in articles:
            # Articles with no abstract are retained as-is
            if not item.abstract_snippet:
                result.append(item)
                continue

            title_sim = _cosine_similarity(
                query_embedding, self._retriever.encode(item.title)
            )
            content_sim = _cosine_similarity(
                query_embedding, self._retriever.encode(item.abstract_snippet)
            )

            mismatch = title_sim - content_sim
            if mismatch > config.mismatch_threshold:
                quality_score = item.score * (1.0 - _clamp(mismatch, 0.0, 1.0))
                if quality_score < config.min_article_score:
                    # Exclude entirely
                    continue
                # Keep with warning and updated score
                item.score = quality_score
                item.quality_warning = warning_text

            result.append(item)

        return result

    def _verify_web_resources(
        self,
        web_resources: list[WebResourceRecommendation],
        query_embedding: np.ndarray,
        warning_text: str,
        config: AppConfig,
    ) -> list[WebResourceRecommendation]:
        result: list[WebResourceRecommendation] = []

        for item in web_resources:
            # Domain blocklist check first
            if _is_domain_blocked(item.url, config.domain_blocklist):
                continue

            # Mismatch check using snippet as content signal
            title_sim = _cosine_similarity(
                query_embedding, self._retriever.encode(item.title)
            )
            content_sim = _cosine_similarity(
                query_embedding, self._retriever.encode(item.snippet)
            )

            mismatch = title_sim - content_sim
            if mismatch > config.mismatch_threshold:
                quality_score = item.web_score * (1.0 - _clamp(mismatch, 0.0, 1.0))
                if quality_score < config.min_web_score:
                    # Exclude entirely
                    continue
                # Keep with warning and updated score
                item.web_score = quality_score
                item.quality_warning = warning_text

            result.append(item)

        return result
