"""AppConfig dataclass — all tuneable parameters for the Hybrid Thesis Recommender."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppConfig:
    # ── Retrieval weights ────────────────────────────────────────────────────
    # Both must be in [0.0, 1.0]
    semantic_weight: float = 0.6
    keyword_weight: float = 0.4

    # ── Top-K limits ─────────────────────────────────────────────────────────
    # All must be >= 1
    article_top_k: int = 10
    web_top_k: int = 10
    semantic_top_k: int = 20
    keyword_top_k: int = 20

    # ── Minimum score thresholds ─────────────────────────────────────────────
    min_article_score: float = 0.1
    min_web_score: float = 0.1

    # ── Embedding model ───────────────────────────────────────────────────────
    embedding_model: str = "paraphrase-multilingual-mpnet-base-v2"

    # ── Storage paths ─────────────────────────────────────────────────────────
    vector_store_path: str = "data/faiss.index"
    metadata_db_path: str = "data/articles.db"
    bm25_index_path: str = "data/bm25.pkl"
    feedback_store_path: str = "data/feedback.db"
    user_store_path: str = "data/users.db"
    secret_key: str = "change-this-in-production-to-a-random-secret"

    # ── Web search ────────────────────────────────────────────────────────────
    # web_search_provider must be one of: "duckduckgo", "google_cse", "bing"
    web_search_provider: str = "duckduckgo"
    web_search_num_results: int = 10
    bilingual_web_search: bool = False
    google_cse_api_key: str = ""
    google_cse_cx: str = ""
    bing_api_key: str = ""

    # ── Language ──────────────────────────────────────────────────────────────
    # default_language must be one of: "ro", "en"
    default_language: str = "en"
    # restrict_language: None means both languages; "ro" or "en" restricts retrieval
    restrict_language: Optional[str] = None

    # ── Timeouts ──────────────────────────────────────────────────────────────
    request_timeout_seconds: float = 5.0
    component_timeout_seconds: float = 3.0

    # ── Content quality / clickbait filtering ────────────────────────────────
    mismatch_threshold: float = 0.3
    domain_blocklist: list = field(default_factory=list)

    # ── Feedback / user ratings ───────────────────────────────────────────────
    feedback_signal_enabled: bool = False
    feedback_signal_boost: float = 0.1
    feedback_signal_min_rating: float = 4.0

    # ── Fusion strategy ───────────────────────────────────────────────────────
    # Must be one of: "rrf", "weighted_sum"
    fusion_strategy: str = "rrf"
