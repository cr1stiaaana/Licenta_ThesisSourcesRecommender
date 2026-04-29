"""Data models for the Hybrid Thesis Recommender."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    """Represents an academic article."""

    id: str  # SHA-256 hash of DOI or normalized title
    title: str
    abstract: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    url: str | None = None
    keywords: list[str] = field(default_factory=list)
    language: str = "en"


@dataclass
class Query:
    """Represents a user query."""

    title: str
    abstract: str | None = None
    keywords: list[str] = field(default_factory=list)

    def combined_text(self) -> str:
        """Return title, abstract, and keywords joined with spaces.

        Only non-None, non-empty parts are included.
        """
        parts = [self.title]
        if self.abstract:
            parts.append(self.abstract)
        if self.keywords:
            parts.append(" ".join(self.keywords))
        return " ".join(parts)


@dataclass
class ScoredArticle:
    """An article with a retrieval score."""

    article: Article
    score: float  # in [0.0, 1.0]


@dataclass
class RetrievalResult:
    """Result from a single retriever."""

    items: list[ScoredArticle] = field(default_factory=list)
    source: str = ""  # e.g. "semantic" or "keyword"


@dataclass
class RawWebResult:
    """Raw result from a web search adapter."""

    title: str
    url: str
    snippet: str = ""
    rank: int = 0
    web_score: float = 0.0
    keywords: list[str] = field(default_factory=list)


@dataclass
class WebRetrievalResult:
    """Result from the web retriever."""

    items: list[RawWebResult] = field(default_factory=list)


@dataclass
class ArticleRecommendation:
    """A ranked article recommendation for the response."""

    resource_type: str = "article"
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    abstract_snippet: str = ""
    score: float = 0.0
    doi: str | None = None
    url: str | None = None
    quality_warning: str | None = None
    item_id: str = ""  # used for feedback


@dataclass
class WebResourceRecommendation:
    """A ranked web resource recommendation."""

    resource_type: str = "web"
    title: str = ""
    url: str = ""
    snippet: str = ""
    web_score: float = 0.0
    keywords: list[str] = field(default_factory=list)
    quality_warning: str | None = None
    item_id: str = ""  # used for feedback


@dataclass
class RecommendResponse:
    """The full API response."""

    query_language: str = "en"
    articles: list[ArticleRecommendation] = field(default_factory=list)
    web_resources: list[WebResourceRecommendation] = field(default_factory=list)
    notices: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class FeedbackEntry:
    """A single feedback record."""

    item_id: str
    session_id: str | None
    query: str
    rating: int  # in [1, 5]
    updated_at: datetime


@dataclass
class FeedbackRequest:
    """Incoming feedback API request."""

    item_id: str
    query: str
    rating: int
    session_id: str | None = None


@dataclass
class FeedbackResponse:
    """Feedback API response."""

    message: str | None = None
    error: str | None = None


@dataclass
class FeedbackQueryResult:
    """Result of querying feedback for an item."""

    item_id: str
    user_rating: int | None = None
    average_rating: float | None = None
    rating_count: int = 0
