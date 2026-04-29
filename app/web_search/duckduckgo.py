"""DuckDuckGo web search adapter using the ddgs library."""

from __future__ import annotations

import logging

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

from app.models import RawWebResult
from app.web_search.base import WebSearchAdapter

logger = logging.getLogger(__name__)


def _normalize_scores(results: list[RawWebResult]) -> list[RawWebResult]:
    """Normalize web_score values so rank 0 receives 1.0."""
    if not results:
        return results
    for r in results:
        r.web_score = 1.0 / (r.rank + 1)
    return results


class DuckDuckGoAdapter(WebSearchAdapter):
    """Web search adapter backed by the ddgs library.

    Uses DDGS.text() which returns real web search results with no API key.

    Requirements: 6.3, 6.4
    """

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = int(timeout)

    def search(self, query: str, num_results: int) -> list[RawWebResult]:
        """Search DuckDuckGo and return up to num_results results."""
        results: list[RawWebResult] = []

        # Cap at 5 to keep latency low — ddgs slows down significantly above 5
        fetch_count = min(num_results, 5)

        with DDGS(timeout=self._timeout) as ddgs:
            hits = list(ddgs.text(query, max_results=fetch_count) or [])

        for rank, hit in enumerate(hits):
            url = hit.get("href", "").strip()
            title = hit.get("title", "").strip()
            snippet = hit.get("body", "").strip()

            if not url:
                continue

            results.append(
                RawWebResult(
                    title=title or url,
                    url=url,
                    snippet=snippet[:300] if snippet else "",
                    rank=rank,
                    web_score=1.0 / (rank + 1),
                )
            )

        return _normalize_scores(results)
