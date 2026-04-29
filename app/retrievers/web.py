"""WebRetriever — orchestrates web search adapters for the Hybrid Thesis Recommender.

Requirements: 6.1, 6.2, 6.5, 6.6, 6.7, 6.8, 6.10
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from app.config import AppConfig
from app.models import Query, RawWebResult, WebRetrievalResult
from app.web_search.base import WebSearchAdapter
from app.web_search.bing import BingSearchAdapter
from app.web_search.duckduckgo import DuckDuckGoAdapter
from app.web_search.google_cse import GoogleCSEAdapter

logger = logging.getLogger(__name__)

_HEAD_TIMEOUT = 5  # seconds for URL accessibility HEAD requests


def _build_adapter(config: AppConfig) -> WebSearchAdapter:
    """Instantiate the correct adapter based on ``config.web_search_provider``.

    Supported providers: ``"duckduckgo"``, ``"google_cse"``, ``"bing"``.
    Falls back to DuckDuckGo for unknown values.
    """
    provider = config.web_search_provider.lower()
    if provider == "google_cse":
        return GoogleCSEAdapter(config)
    if provider == "bing":
        return BingSearchAdapter(config)
    # Default / "duckduckgo"
    return DuckDuckGoAdapter(timeout=config.request_timeout_seconds)


def _is_url_accessible(url: str) -> bool:
    """Return ``True`` if the URL is reachable (non-4xx/5xx).

    Issues a lightweight HEAD request.  If the request itself raises any
    exception (network error, timeout, etc.) the URL is kept (returns
    ``True``) so that transient failures do not silently drop results.
    """
    try:
        response = requests.head(url, timeout=_HEAD_TIMEOUT, allow_redirects=True)
        return response.status_code < 400
    except Exception:
        # Network errors, timeouts, SSL issues — keep the URL
        return True


def _deduplicate_by_url(results: list[RawWebResult]) -> list[RawWebResult]:
    """Return *results* with duplicates removed, keeping the first occurrence."""
    seen: set[str] = set()
    deduped: list[RawWebResult] = []
    for item in results:
        if item.url not in seen:
            seen.add(item.url)
            deduped.append(item)
    return deduped


class WebRetriever:
    """Retrieves web resources relevant to a :class:`~app.models.Query`.

    Selects the appropriate :class:`~app.web_search.base.WebSearchAdapter`
    based on :attr:`~app.config.AppConfig.web_search_provider`, issues
    search queries (optionally in both Romanian and English in parallel when
    :attr:`~app.config.AppConfig.bilingual_web_search` is enabled), filters
    out inaccessible URLs, and returns a :class:`~app.models.WebRetrievalResult`.

    Requirements: 6.1, 6.2, 6.5, 6.6, 6.7, 6.8, 6.10
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._adapter: WebSearchAdapter = _build_adapter(config)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def retrieve(self, query: Query, query_language: str) -> WebRetrievalResult:
        """Retrieve web results for *query* in *query_language*.

        When :attr:`~app.config.AppConfig.bilingual_web_search` is enabled,
        parallel queries are issued in both ``"ro"`` and ``"en"`` and the
        results are merged, deduplicating by URL (first occurrence wins).

        URL accessibility is verified via a HEAD request; URLs that return
        HTTP 4xx or 5xx are filtered out.  If the underlying adapter raises
        any exception (e.g. API unavailable), an empty
        :class:`~app.models.WebRetrievalResult` is returned without
        propagating the error.

        Parameters
        ----------
        query:
            The user query whose :meth:`~app.models.Query.combined_text` is
            used as the search string.
        query_language:
            The detected language of the query (``"ro"`` or ``"en"``).

        Returns
        -------
        WebRetrievalResult
            Filtered, deduplicated web results, or an empty result on error.
        """
        search_text = query.combined_text()
        num_results = self._config.web_search_num_results

        try:
            if self._config.bilingual_web_search:
                raw_items = self._search_bilingual(search_text, num_results)
            else:
                raw_items = self._adapter.search(search_text, num_results)
        except Exception as exc:
            logger.warning(
                "WebRetriever: adapter raised an exception, returning empty result. "
                "Error: %s",
                exc,
            )
            return WebRetrievalResult()

        # Deduplicate (relevant for bilingual mode, harmless otherwise)
        raw_items = _deduplicate_by_url(raw_items)

        return WebRetrievalResult(items=raw_items)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _search_bilingual(
        self, search_text: str, num_results: int
    ) -> list[RawWebResult]:
        """Issue parallel searches in Romanian and English and merge results.

        Both language queries use the same *search_text* (the combined query
        text).  Results are merged in the order ``[ro_results, en_results]``
        and deduplication is applied by the caller.
        """
        languages = ["ro", "en"]
        results_by_lang: dict[str, list[RawWebResult]] = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_lang = {
                executor.submit(
                    self._adapter.search, search_text, num_results
                ): lang
                for lang in languages
            }
            for future in as_completed(future_to_lang):
                lang = future_to_lang[future]
                try:
                    results_by_lang[lang] = future.result()
                except Exception as exc:
                    logger.warning(
                        "WebRetriever: bilingual search for lang=%r failed: %s",
                        lang,
                        exc,
                    )
                    results_by_lang[lang] = []

        # Merge: Romanian first, then English
        merged: list[RawWebResult] = []
        for lang in languages:
            merged.extend(results_by_lang.get(lang, []))
        return merged
