"""Bing Web Search API v7 adapter."""

from __future__ import annotations

import logging

import requests

from app.config import AppConfig
from app.models import RawWebResult
from app.web_search.base import WebSearchAdapter

logger = logging.getLogger(__name__)

_BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"


def _normalize_scores(results: list[RawWebResult]) -> list[RawWebResult]:
    """Normalize ``web_score`` so rank 0 receives 1.0."""
    if not results:
        return results
    max_raw = 1.0 / (0 + 1)  # 1.0
    for r in results:
        raw = 1.0 / (r.rank + 1)
        r.web_score = raw / max_raw
    return results


class BingSearchAdapter(WebSearchAdapter):
    """Web search adapter backed by the Bing Web Search API v7.

    The subscription key is read from
    :attr:`~app.config.AppConfig.bing_api_key` and sent via the
    ``Ocp-Apim-Subscription-Key`` request header.

    Requirements: 6.9
    """

    def __init__(self, config: AppConfig) -> None:
        self._api_key = config.bing_api_key
        self._timeout = config.request_timeout_seconds

    def search(self, query: str, num_results: int) -> list[RawWebResult]:
        """Search via Bing Web Search and return up to *num_results* results.

        Parameters
        ----------
        query:
            Search query string.
        num_results:
            Maximum number of results to return.

        Returns
        -------
        list[RawWebResult]
            Results with rank-based ``web_score`` normalised to ``[0, 1]``.

        Raises
        ------
        requests.HTTPError
            On a non-2xx HTTP response.
        requests.RequestException
            On any network-level error.
        """
        headers = {"Ocp-Apim-Subscription-Key": self._api_key}
        params: dict[str, str | int] = {
            "q": query,
            "count": num_results,
            "responseFilter": "Webpages",
        }
        response = requests.get(
            _BING_SEARCH_URL,
            headers=headers,
            params=params,
            timeout=self._timeout,
        )
        response.raise_for_status()

        data = response.json()
        web_pages: dict = data.get("webPages", {})
        items: list[dict] = web_pages.get("value", [])

        results: list[RawWebResult] = []
        for rank, item in enumerate(items[:num_results]):
            title: str = item.get("name", "").strip()
            url: str = item.get("url", "").strip()
            snippet: str = item.get("snippet", "").strip()

            if not url:
                continue

            results.append(
                RawWebResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    rank=rank,
                    web_score=1.0 / (rank + 1),  # normalised below
                )
            )

        return _normalize_scores(results)
