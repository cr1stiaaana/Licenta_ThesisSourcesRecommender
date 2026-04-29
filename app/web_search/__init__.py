"""Web search adapters for the Hybrid Thesis Recommender."""

from app.web_search.base import WebSearchAdapter
from app.web_search.bing import BingSearchAdapter
from app.web_search.duckduckgo import DuckDuckGoAdapter
from app.web_search.google_cse import GoogleCSEAdapter

__all__ = [
    "WebSearchAdapter",
    "DuckDuckGoAdapter",
    "GoogleCSEAdapter",
    "BingSearchAdapter",
]
