"""Google Custom Search Engine (CSE) adapter."""

from __future__ import annotations

import logging

import requests

from app.config import AppConfig
from app.models import RawWebResult
from app.web_search.base import WebSearchAdapter

logger = logging.getLogger(__name__)

_GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"


def _normalize_scores(results: list[RawWebResult]) -> list[RawWebResult]:
    """Normalize ``web_score`` so rank 0 receives 1.0."""
    if not results:
        return results
    max_raw = 1.0 / (0 + 1)  # 1.0
    for r in results:
        raw = 1.0 / (r.rank + 1)
        r.web_score = raw / max_raw
    return results


class GoogleCSEAdapter(WebSearchAdapter):
    """Web search adapter backed by the Google Custom Search API.

    Credentials are read from :class:`~app.config.AppConfig`:

    * ``google_cse_api_key`` — API key
    * ``google_cse_cx`` — Custom Search Engine ID

    Requirements: 6.9
    """

    def __init__(self, config: AppConfig) -> None:
        self._api_key = config.google_cse_api_key
        self._cx = config.google_cse_cx
        self._timeout = config.request_timeout_seconds

    def search(self, query: str, num_results: int) -> list[RawWebResult]:
        """Search via Google CSE and return up to *num_results* results.

        Parameters
        ----------
        query:
            Search query string.
        num_results:
            Maximum number of results to return (capped at 10 per API page).

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
        # Google CSE returns at most 10 results per request.
        num = min(num_results, 10)
        params: dict[str, str | int] = {
            "key": self._api_key,
            "cx": self._cx,
            "q": query,
            "num": num,
        }
        response = requests.get(
            _GOOGLE_CSE_URL,
            params=params,
            timeout=self._timeout,
        )
        response.raise_for_status()

        data = response.json()
        items: list[dict] = data.get("items", [])

        results: list[RawWebResult] = []
        for rank, item in enumerate(items[:num_results]):
            title: str = item.get("title", "").strip()
            url: str = item.get("link", "").strip()
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
