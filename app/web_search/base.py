"""Abstract base class for web search adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import RawWebResult


class WebSearchAdapter(ABC):
    """Abstract interface for web search backends.

    All concrete adapters must implement :meth:`search` and return a list of
    :class:`~app.models.RawWebResult` objects ordered by relevance rank.
    """

    @abstractmethod
    def search(self, query: str, num_results: int) -> list[RawWebResult]:
        """Execute a web search and return ranked results.

        Parameters
        ----------
        query:
            The search query string.
        num_results:
            Maximum number of results to return.

        Returns
        -------
        list[RawWebResult]
            Results ordered by rank (rank 0 = most relevant).  Each result
            carries a ``web_score`` normalised so that rank 0 receives 1.0.

        Raises
        ------
        Exception
            Any HTTP or network error is propagated to the caller
            (:class:`~app.retrievers.web.WebRetriever`) which handles it
            gracefully.
        """
