"""Flask REST API for the Hybrid Thesis Recommender.

Implements:
  - Application factory ``create_app(config_manager, article_store=None)``
  - ``POST /recommend``  — hybrid retrieval endpoint
  - ``POST /feedback``   — submit a rating
  - ``GET  /feedback/<item_id>`` — query ratings for an item
  - ``GET  /``           — serve static index.html

Requirements: 1.1–1.5, 4.1–4.3, 5.1–5.4, 5.6, 5.9–5.12,
              9.1–9.6, 11.1, 11.3, 11.4, 11.12,
              12.1–12.3, 12.5, 12.6, 12.11–12.13
"""

from __future__ import annotations

import concurrent.futures
import dataclasses
import logging
import string
from datetime import datetime, timezone
from typing import Any

from flask import Blueprint, Flask, jsonify, request, send_from_directory, session

from app.auth import User, UserStore, UserStoreError
from app.config_manager import ConfigManager
from app.feedback.store import FeedbackStore, FeedbackStoreError
from app.language_detector import LanguageDetector
from app.models import (
    ArticleRecommendation,
    FeedbackQueryResult,
    Query,
    RecommendResponse,
    RetrievalResult,
    WebResourceRecommendation,
    WebRetrievalResult,
)
from app.i18n import t
from app.rankers.hybrid import HybridRanker
from app.retrievers.keyword import KeywordRetriever, KeywordRetrieverError
from app.retrievers.semantic import SemanticRetriever, SemanticRetrieverError
from app.retrievers.web import WebRetriever
from app.retrievers.academic_web import AcademicWebRetriever
from app.verifiers.content import ContentVerifier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JSON serialization helpers
# ---------------------------------------------------------------------------

def _serialize_recommendation(rec: Any) -> dict:
    """Convert a recommendation dataclass to a dict, omitting None quality_warning."""
    d = dataclasses.asdict(rec)
    if d.get("quality_warning") is None:
        d.pop("quality_warning", None)
    return d


def _serialize_response(resp: RecommendResponse) -> dict:
    """Serialize a RecommendResponse to a JSON-safe dict."""
    return {
        "query_language": resp.query_language,
        "articles": [_serialize_recommendation(a) for a in resp.articles],
        "web_resources": [_serialize_recommendation(w) for w in resp.web_resources],
        "notices": resp.notices,
        **({"error": resp.error} if resp.error is not None else {}),
    }


def _serialize_feedback_result(result: FeedbackQueryResult) -> dict:
    """Serialize a FeedbackQueryResult to a JSON-safe dict."""
    d: dict = {"item_id": result.item_id, "rating_count": result.rating_count}
    if result.user_rating is not None:
        d["user_rating"] = result.user_rating
    if result.average_rating is not None:
        d["average_rating"] = result.average_rating
    return d


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

_PUNCTUATION_SET = set(string.punctuation + string.whitespace)


def _validate_title(title: str) -> str | None:
    """Return an error key if *title* is invalid, else None.

    Rules:
    - After stripping whitespace: length must be in [3, 500].
    - Must contain at least one character that is neither whitespace nor punctuation.
    """
    stripped = title.strip()
    if len(stripped) < 3 or len(stripped) > 500:
        return "query_invalid"
    # Must have at least one non-whitespace, non-punctuation character
    if not any(ch not in _PUNCTUATION_SET for ch in stripped):
        return "query_invalid"
    return None


# ---------------------------------------------------------------------------
# Blueprint factories
# ---------------------------------------------------------------------------

def _make_recommend_blueprint(
    language_detector: LanguageDetector,
    semantic_retriever: SemanticRetriever | None,
    keyword_retriever: KeywordRetriever | None,
    academic_web_retriever: AcademicWebRetriever,
    web_retriever: WebRetriever,
    hybrid_ranker: HybridRanker,
    content_verifier: ContentVerifier | None,
    config_manager: ConfigManager,
) -> Blueprint:
    bp = Blueprint("recommend", __name__)

    @bp.route("/recommend", methods=["POST"])
    def recommend():  # type: ignore[return]
        cfg = config_manager.get()
        data = request.get_json(silent=True) or {}

        # ── Validate title ────────────────────────────────────────────────
        raw_title: str = data.get("title", "")
        if not isinstance(raw_title, str):
            raw_title = str(raw_title)

        # ── Get offset for pagination ─────────────────────────────────────
        offset: int = data.get("offset", 0)
        if not isinstance(offset, int) or offset < 0:
            offset = 0

        error_key = _validate_title(raw_title)
        if error_key:
            # Detect language for the error message (best-effort)
            try:
                err_lang = language_detector.detect(raw_title.strip()) if raw_title.strip() else "en"
            except Exception:
                err_lang = "en"
            return jsonify({"error": t(error_key, err_lang)}), 422

        title = raw_title.strip()
        abstract: str | None = data.get("abstract") or None
        keywords: list[str] = data.get("keywords") or []
        if not isinstance(keywords, list):
            keywords = []

        # ── Detect language ───────────────────────────────────────────────
        try:
            query_language = language_detector.detect(title)
        except Exception:
            query_language = "en"

        query = Query(title=title, abstract=abstract, keywords=keywords)
        notices: list[str] = []

        # ── Run retrievers in parallel ────────────────────────────────────
        semantic_result: RetrievalResult | None = None
        keyword_result: RetrievalResult | None = None
        academic_web_result: RetrievalResult | None = None
        web_result: WebRetrievalResult = WebRetrievalResult()

        timeout = cfg.component_timeout_seconds

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures: dict[str, concurrent.futures.Future] = {}

            if semantic_retriever is not None:
                futures["semantic"] = executor.submit(
                    semantic_retriever.retrieve, query, cfg.semantic_top_k
                )
            if keyword_retriever is not None:
                futures["keyword"] = executor.submit(
                    keyword_retriever.retrieve, query, cfg.keyword_top_k
                )
            futures["academic_web"] = executor.submit(
                academic_web_retriever.retrieve, query, cfg.article_top_k
            )
            futures["web"] = executor.submit(
                web_retriever.retrieve, query, query_language
            )

            for name, future in futures.items():
                try:
                    result = future.result(timeout=timeout)
                    if name == "semantic":
                        semantic_result = result
                    elif name == "keyword":
                        keyword_result = result
                    elif name == "academic_web":
                        academic_web_result = result
                    elif name == "web":
                        web_result = result
                except SemanticRetrieverError as exc:
                    logger.warning("SemanticRetriever failed: %s", exc)
                    notices.append(t("semantic_unavailable", query_language))
                except KeywordRetrieverError as exc:
                    logger.warning("KeywordRetriever failed: %s", exc)
                    notices.append(t("keyword_unavailable", query_language))
                except concurrent.futures.TimeoutError:
                    logger.warning("Retriever '%s' timed out after %.1fs", name, timeout)
                    if name == "semantic":
                        notices.append(t("semantic_unavailable", query_language))
                    elif name == "keyword":
                        notices.append(t("keyword_unavailable", query_language))
                    elif name == "web":
                        notices.append(t("web_unavailable", query_language))
                except Exception as exc:
                    logger.warning("Retriever '%s' raised unexpected error: %s", name, exc)
                    if name == "semantic":
                        notices.append(t("semantic_unavailable", query_language))
                    elif name == "keyword":
                        notices.append(t("keyword_unavailable", query_language))
                    elif name == "web":
                        notices.append(t("web_unavailable", query_language))

        # ── Merge academic_web_result with semantic/keyword ───────────────
        # Treat academic_web as another article source
        if academic_web_result is not None and academic_web_result.items:
            if semantic_result is None:
                semantic_result = academic_web_result
            else:
                # Merge academic_web into semantic
                semantic_result.items.extend(academic_web_result.items)

        # ── Both article retrievers failed → HTTP 500 ─────────────────────
        if semantic_result is None and keyword_result is None:
            resp = RecommendResponse(
                query_language=query_language,
                notices=notices,
                error="All article retrievers are unavailable.",
            )
            return jsonify(_serialize_response(resp)), 500

        # ── Fuse articles ─────────────────────────────────────────────────
        sem = semantic_result if semantic_result is not None else RetrievalResult(source="semantic")
        kw = keyword_result if keyword_result is not None else RetrievalResult(source="keyword")

        # Get more results than needed to allow pagination
        fetch_count = cfg.article_top_k + offset + 10  # Fetch extra to ensure we have enough

        all_articles: list[ArticleRecommendation] = hybrid_ranker.fuse_articles(
            semantic=sem,
            keyword=kw,
            top_k=fetch_count,
            semantic_weight=cfg.semantic_weight,
            keyword_weight=cfg.keyword_weight,
        )
        
        # Apply offset and limit
        articles = all_articles[offset:offset + cfg.article_top_k]

        # ── Rank web resources ────────────────────────────────────────────
        fetch_web_count = cfg.web_top_k + offset + 10
        all_web_resources: list[WebResourceRecommendation] = hybrid_ranker.rank_web_resources(
            web=web_result,
            top_k=fetch_web_count,
        )
        
        # Apply offset and limit
        web_resources = all_web_resources[offset:offset + cfg.web_top_k]

        # ── Content verification ──────────────────────────────────────────
        if content_verifier is not None and semantic_retriever is not None:
            try:
                query_embedding = semantic_retriever.encode(query.combined_text())
                articles, web_resources = content_verifier.verify(
                    articles=articles,
                    web_resources=web_resources,
                    query_embedding=query_embedding,
                    query_language=query_language,
                    config=cfg,
                )
            except Exception as exc:
                logger.warning("ContentVerifier failed: %s", exc)

        # ── Build and return response ─────────────────────────────────────
        response = RecommendResponse(
            query_language=query_language,
            articles=articles,
            web_resources=web_resources,
            notices=notices,
        )
        return jsonify(_serialize_response(response)), 200

    return bp


def _make_feedback_blueprint(
    language_detector: LanguageDetector,
    feedback_store: FeedbackStore,
) -> Blueprint:
    bp = Blueprint("feedback", __name__)

    @bp.route("/feedback", methods=["POST"])
    def submit_feedback():  # type: ignore[return]
        data = request.get_json(silent=True) or {}

        # ── Detect language for localized messages ────────────────────────
        query_field: str = data.get("query", "")
        if not isinstance(query_field, str):
            query_field = str(query_field)
        try:
            lang = language_detector.detect(query_field) if query_field.strip() else "en"
        except Exception:
            lang = "en"

        # ── Validate item_id ──────────────────────────────────────────────
        item_id = data.get("item_id", "")
        if not isinstance(item_id, str) or not item_id.strip():
            return jsonify({"error": "item_id is required and must be a non-empty string."}), 422

        # ── Validate query ────────────────────────────────────────────────
        if not query_field.strip():
            return jsonify({"error": "query is required and must be a non-empty string."}), 422

        # ── Validate rating ───────────────────────────────────────────────
        raw_rating = data.get("rating")
        try:
            rating = int(raw_rating)
            if rating < 1 or rating > 5:
                raise ValueError("out of range")
        except (TypeError, ValueError):
            return jsonify({"error": t("rating_invalid", lang)}), 422

        # ── Optional session_id ───────────────────────────────────────────
        session_id: str | None = data.get("session_id") or None
        if session_id is not None and not isinstance(session_id, str):
            session_id = str(session_id)

        # ── Persist rating ────────────────────────────────────────────────
        try:
            feedback_store.upsert_rating(
                item_id=item_id.strip(),
                query=query_field,
                rating=rating,
                session_id=session_id,
                timestamp=datetime.now(tz=timezone.utc),
            )
        except FeedbackStoreError as exc:
            logger.error("FeedbackStore.upsert_rating failed: %s", exc)
            return jsonify({"error": str(exc)}), 503

        return jsonify({"message": t("rating_saved", lang)}), 200

    @bp.route("/feedback/<item_id>", methods=["GET"])
    def get_feedback(item_id: str):  # type: ignore[return]
        session_id: str | None = request.args.get("session_id") or None

        try:
            result: FeedbackQueryResult = feedback_store.get_ratings(
                item_id=item_id,
                session_id=session_id,
            )
        except FeedbackStoreError as exc:
            logger.error("FeedbackStore.get_ratings failed: %s", exc)
            return jsonify({"error": str(exc)}), 503

        return jsonify(_serialize_feedback_result(result)), 200

    return bp


def _make_auth_blueprint(user_store: UserStore) -> Blueprint:
    """Create authentication blueprint with register, login, logout, saved items routes."""
    bp = Blueprint("auth", __name__)

    @bp.route("/auth/register", methods=["POST"])
    def register():
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not username or len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 422
        if not email or "@" not in email:
            return jsonify({"error": "Valid email is required"}), 422
        if not password or len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 422

        try:
            user = user_store.create_user(username, email, password)
            session["user_id"] = user.id
            session["username"] = user.username
            return jsonify({"message": "Registration successful", "user": {"id": user.id, "username": user.username}}), 201
        except UserStoreError as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.route("/auth/login", methods=["POST"])
    def login():
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 422

        user = user_store.authenticate(username, password)
        if user is None:
            return jsonify({"error": "Invalid username or password"}), 401

        session["user_id"] = user.id
        session["username"] = user.username
        return jsonify({"message": "Login successful", "user": {"id": user.id, "username": user.username}}), 200

    @bp.route("/auth/logout", methods=["POST"])
    def logout():
        session.clear()
        return jsonify({"message": "Logout successful"}), 200

    @bp.route("/auth/me", methods=["GET"])
    def get_current_user():
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"user": None}), 200

        user = user_store.get_user_by_id(user_id)
        if user is None:
            session.clear()
            return jsonify({"user": None}), 200

        return jsonify({"user": {"id": user.id, "username": user.username, "email": user.email}}), 200

    @bp.route("/saved", methods=["GET"])
    def get_saved_items():
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "Not authenticated"}), 401

        items = user_store.get_saved_items(user_id)
        return jsonify({"items": items}), 200

    @bp.route("/saved", methods=["POST"])
    def save_item():
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "Not authenticated"}), 401

        data = request.get_json(silent=True) or {}
        item_id = data.get("item_id", "").strip()
        item_data = data.get("item_data")

        if not item_id or not item_data:
            return jsonify({"error": "item_id and item_data are required"}), 422

        user_store.save_item(user_id, item_id, item_data)
        return jsonify({"message": "Item saved"}), 200

    @bp.route("/saved/<item_id>", methods=["DELETE"])
    def unsave_item(item_id: str):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "Not authenticated"}), 401

        user_store.unsave_item(user_id, item_id)
        return jsonify({"message": "Item removed"}), 200

    @bp.route("/saved/<item_id>/check", methods=["GET"])
    def check_saved(item_id: str):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"saved": False}), 200

        saved = user_store.is_item_saved(user_id, item_id)
        return jsonify({"saved": saved}), 200

    return bp


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(
    config_manager: ConfigManager,
    article_store=None,  # ArticleStore | None — injected for testing
) -> Flask:
    """Create and configure the Flask application.

    Initializes all application-scoped singletons at startup:
    ``LanguageDetector``, ``SemanticRetriever``, ``KeywordRetriever``,
    ``WebRetriever``, ``HybridRanker``, ``ContentVerifier``, ``FeedbackStore``.

    Args:
        config_manager: Provides the live ``AppConfig`` snapshot.
        article_store:  Optional pre-built ``ArticleStore`` (for testing).
                        When ``None``, an ``ArticleStore`` is created from config.

    Returns:
        A configured Flask application instance.
    """
    import os

    cfg = config_manager.get()

    # ── Static files ──────────────────────────────────────────────────────
    # Resolve the static folder relative to this file so it works regardless
    # of the working directory.
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    app = Flask(__name__, static_folder=static_folder, static_url_path="/static")
    app.secret_key = cfg.secret_key  # For session management

    # ── ArticleStore ──────────────────────────────────────────────────────
    if article_store is None:
        from app.article_store import ArticleStore

        article_store = ArticleStore(
            vector_store_path=cfg.vector_store_path,
            metadata_db_path=cfg.metadata_db_path,
        )

    # ── LanguageDetector ──────────────────────────────────────────────────
    language_detector = LanguageDetector()

    # ── SemanticRetriever ─────────────────────────────────────────────────
    semantic_retriever: SemanticRetriever | None = None
    try:
        semantic_retriever = SemanticRetriever(article_store, cfg)
        logger.info("SemanticRetriever initialized successfully.")
    except SemanticRetrieverError as exc:
        logger.error("SemanticRetriever failed to initialize: %s — semantic retrieval disabled.", exc)

    # ── KeywordRetriever ──────────────────────────────────────────────────
    keyword_retriever: KeywordRetriever | None = None
    try:
        keyword_retriever = KeywordRetriever(article_store, cfg)
        logger.info("KeywordRetriever initialized successfully.")
    except KeywordRetrieverError as exc:
        logger.error("KeywordRetriever failed to initialize: %s — keyword retrieval disabled.", exc)

    # ── WebRetriever ──────────────────────────────────────────────────────
    web_retriever = WebRetriever(cfg)

    # ── AcademicWebRetriever ──────────────────────────────────────────────
    academic_web_retriever = AcademicWebRetriever(timeout=cfg.component_timeout_seconds)

    # ── FeedbackStore ─────────────────────────────────────────────────────
    feedback_store = FeedbackStore(cfg.feedback_store_path)

    # ── HybridRanker ──────────────────────────────────────────────────────
    hybrid_ranker = HybridRanker(cfg, feedback_store=feedback_store)

    # ── ContentVerifier ───────────────────────────────────────────────────
    content_verifier: ContentVerifier | None = None
    if semantic_retriever is not None:
        content_verifier = ContentVerifier(semantic_retriever)

    # ── Register blueprints ───────────────────────────────────────────────
    recommend_bp = _make_recommend_blueprint(
        language_detector=language_detector,
        semantic_retriever=semantic_retriever,
        keyword_retriever=keyword_retriever,
        academic_web_retriever=academic_web_retriever,
        web_retriever=web_retriever,
        hybrid_ranker=hybrid_ranker,
        content_verifier=content_verifier,
        config_manager=config_manager,
    )
    feedback_bp = _make_feedback_blueprint(
        language_detector=language_detector,
        feedback_store=feedback_store,
    )

    app.register_blueprint(recommend_bp)
    app.register_blueprint(feedback_bp)

    # ── Auth blueprint ────────────────────────────────────────────────────
    user_store = UserStore(cfg.user_store_path)
    auth_bp = _make_auth_blueprint(user_store)
    app.register_blueprint(auth_bp)

    # ── Root route — serve index.html ─────────────────────────────────────
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    return app
