"""Integration tests for the Hybrid Thesis Recommender.

Tests:
  1. End-to-end POST /recommend with a small in-memory article corpus
  2. POST /feedback -> GET /feedback/{item_id} round-trip
  3. ContentVerifier with real embedding model -- blocklisted domain excluded
  4. ContentVerifier with real embedding model -- flagged item carries localized warning

Requirements: 5.1, 5.2, 5.4, 5.10, 12.2, 12.5, 5b.9, 5b.11, 5b.12
"""

from __future__ import annotations

import hashlib
import os
import pickle
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.article_store import ArticleStore
from app.config import AppConfig
from app.config_manager import ConfigManager
from app.feedback.store import FeedbackStore
from app.models import (
    Article,
    ArticleRecommendation,
    RawWebResult,
    RetrievalResult,
    ScoredArticle,
    WebResourceRecommendation,
    WebRetrievalResult,
)

# ---------------------------------------------------------------------------
# Constants / helpers
# ---------------------------------------------------------------------------

_EMBEDDING_DIM = 768


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _random_embedding(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(_EMBEDDING_DIM).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return vec


def _make_mock_semantic_retriever(articles: list[Article]) -> MagicMock:
    """Return a mock SemanticRetriever that returns all articles with score 0.8."""
    mock = MagicMock()
    mock.encode.return_value = _random_embedding(seed=42)
    scored = [ScoredArticle(article=a, score=0.8) for a in articles]
    mock.retrieve.return_value = RetrievalResult(items=scored, source="semantic")
    return mock


def _make_mock_web_result() -> WebRetrievalResult:
    return WebRetrievalResult(
        items=[
            RawWebResult(
                title="Deep Learning Tutorial",
                url="https://example.com/dl-tutorial",
                snippet="A tutorial on deep learning fundamentals.",
                rank=1,
                web_score=0.9,
            ),
            RawWebResult(
                title="Machine Learning Guide",
                url="https://example.com/ml-guide",
                snippet="Comprehensive guide to machine learning.",
                rank=2,
                web_score=0.7,
            ),
        ]
    )


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_dirs(tmp_path):
    """Provide a temporary directory for FAISS index, SQLite DB, and BM25 index.

    Uses pytest's built-in tmp_path fixture which handles Windows file-lock
    cleanup gracefully (ignores PermissionError on teardown).
    """
    yield str(tmp_path)


@pytest.fixture()
def sample_articles() -> list[Article]:
    return [
        Article(
            id=_sha256("neural networks deep learning"),
            title="Neural Networks for Deep Learning",
            abstract="A comprehensive study of neural network architectures for deep learning tasks.",
            authors=["Alice Smith"],
            year=2022,
            doi="10.1234/nn-dl",
            language="en",
        ),
        Article(
            id=_sha256("natural language processing transformers"),
            title="Natural Language Processing with Transformers",
            abstract="Transformer models have revolutionized natural language processing benchmarks.",
            authors=["Bob Jones"],
            year=2021,
            doi="10.1234/nlp-transformers",
            language="en",
        ),
        Article(
            id=_sha256("computer vision convolutional"),
            title="Computer Vision Using Convolutional Networks",
            abstract="Convolutional neural networks achieve state-of-the-art results in image recognition.",
            authors=["Carol White"],
            year=2020,
            doi="10.1234/cv-cnn",
            language="en",
        ),
        Article(
            id=_sha256("reinforcement learning policy gradient"),
            title="Reinforcement Learning with Policy Gradients",
            abstract="Policy gradient methods enable agents to learn complex behaviors through reward signals.",
            authors=["Dave Brown"],
            year=2023,
            doi="10.1234/rl-pg",
            language="en",
        ),
    ]


@pytest.fixture()
def article_store_with_corpus(tmp_dirs, sample_articles):
    """ArticleStore pre-populated with sample articles using random embeddings."""
    store = ArticleStore(
        vector_store_path=os.path.join(tmp_dirs, "faiss.index"),
        metadata_db_path=os.path.join(tmp_dirs, "articles.db"),
    )
    for i, article in enumerate(sample_articles):
        store.add_article(article, _random_embedding(seed=i))

    # Build and persist a BM25 index so KeywordRetriever can load it
    from rank_bm25 import BM25Okapi

    corpus = store.get_all_texts()
    bm25 = BM25Okapi(corpus)
    bm25_path = os.path.join(tmp_dirs, "bm25.pkl")
    with open(bm25_path, "wb") as fh:
        pickle.dump(bm25, fh)

    return store


@pytest.fixture()
def app_config(tmp_dirs):
    """AppConfig pointing to temp paths with permissive thresholds."""
    return AppConfig(
        vector_store_path=os.path.join(tmp_dirs, "faiss.index"),
        metadata_db_path=os.path.join(tmp_dirs, "articles.db"),
        bm25_index_path=os.path.join(tmp_dirs, "bm25.pkl"),
        feedback_store_path=os.path.join(tmp_dirs, "feedback.db"),
        min_article_score=0.0,
        min_web_score=0.0,
        component_timeout_seconds=30.0,
    )


@pytest.fixture()
def mock_config_manager(app_config):
    """ConfigManager mock whose get() returns app_config."""
    manager = MagicMock(spec=ConfigManager)
    manager.get.return_value = app_config
    return manager


# ---------------------------------------------------------------------------
# Test 1: End-to-end POST /recommend
# ---------------------------------------------------------------------------


class TestRecommendEndToEnd:
    """End-to-end POST /recommend with a small in-memory article corpus.

    The SemanticRetriever is mocked to avoid loading the embedding model.
    The WebRetriever is mocked to avoid real HTTP calls.
    Requirements: 5.1, 5.2, 5.4, 5.10
    """

    @pytest.fixture()
    def flask_client(self, mock_config_manager, article_store_with_corpus, sample_articles):
        """Flask test client with mocked SemanticRetriever and WebRetriever."""
        from app.api import create_app

        mock_semantic = _make_mock_semantic_retriever(sample_articles)

        # Patch SemanticRetriever as imported in app.api so the constructor
        # returns our mock without loading the real embedding model.
        with patch("app.api.SemanticRetriever", return_value=mock_semantic):
            with patch(
                "app.retrievers.web.WebRetriever.retrieve",
                return_value=_make_mock_web_result(),
            ):
                flask_app = create_app(
                    config_manager=mock_config_manager,
                    article_store=article_store_with_corpus,
                )
                yield flask_app.test_client()

    def test_response_structure(self, flask_client):
        """POST /recommend returns the expected top-level fields.

        Requirements: 5.1, 5.2
        """
        resp = flask_client.post(
            "/recommend",
            json={"title": "deep learning neural networks"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert "articles" in data, "Response must contain 'articles'"
        assert "web_resources" in data, "Response must contain 'web_resources'"
        assert "query_language" in data, "Response must contain 'query_language'"
        assert "notices" in data, "Response must contain 'notices'"

        assert isinstance(data["articles"], list)
        assert isinstance(data["web_resources"], list)
        assert isinstance(data["query_language"], str)
        assert isinstance(data["notices"], list)

    def test_article_scores_in_range(self, flask_client):
        """All article scores must be in [0.0, 1.0].

        Requirements: 5.4
        """
        resp = flask_client.post(
            "/recommend",
            json={"title": "deep learning neural networks"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert len(data["articles"]) > 0, "Expected at least one article in response"
        for article in data["articles"]:
            score = article["score"]
            assert 0.0 <= score <= 1.0, (
                f"Article score {score} is outside [0.0, 1.0] for '{article.get('title')}'"
            )

    def test_web_resource_scores_in_range(self, flask_client):
        """All web_resource web_scores must be in [0.0, 1.0].

        Requirements: 5.4
        """
        resp = flask_client.post(
            "/recommend",
            json={"title": "deep learning neural networks"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert len(data["web_resources"]) > 0, "Expected at least one web resource in response"
        for web in data["web_resources"]:
            score = web["web_score"]
            assert 0.0 <= score <= 1.0, (
                f"Web score {score} is outside [0.0, 1.0] for '{web.get('title')}'"
            )

    def test_resource_type_labels(self, flask_client):
        """resource_type must be 'article' for articles and 'web' for web resources.

        Requirements: 5.10
        """
        resp = flask_client.post(
            "/recommend",
            json={"title": "deep learning neural networks"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()

        for article in data["articles"]:
            assert article["resource_type"] == "article", (
                f"Expected resource_type='article', got {article['resource_type']!r}"
            )
        for web in data["web_resources"]:
            assert web["resource_type"] == "web", (
                f"Expected resource_type='web', got {web['resource_type']!r}"
            )

    def test_quality_warning_never_null(self, flask_client):
        """quality_warning must be absent or a non-empty string -- never null/None in JSON.

        Requirements: 5.10
        """
        resp = flask_client.post(
            "/recommend",
            json={"title": "deep learning neural networks"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()

        for item in data["articles"] + data["web_resources"]:
            if "quality_warning" in item:
                assert item["quality_warning"] is not None, (
                    "quality_warning must not be null when present in JSON"
                )
                assert isinstance(item["quality_warning"], str) and item["quality_warning"], (
                    "quality_warning must be a non-empty string when present"
                )

    def test_invalid_title_returns_422(self, flask_client):
        """POST /recommend with a too-short title returns HTTP 422."""
        resp = flask_client.post(
            "/recommend",
            json={"title": "ab"},
            content_type="application/json",
        )
        assert resp.status_code == 422

    def test_whitespace_only_title_returns_422(self, flask_client):
        """POST /recommend with a whitespace-only title returns HTTP 422."""
        resp = flask_client.post(
            "/recommend",
            json={"title": "   "},
            content_type="application/json",
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Test 2: POST /feedback -> GET /feedback/{item_id} round-trip
# ---------------------------------------------------------------------------


class TestFeedbackRoundTrip:
    """POST /feedback -> GET /feedback/{item_id} round-trip against a real SQLite FeedbackStore.

    Requirements: 12.2, 12.5
    """

    @pytest.fixture()
    def feedback_client(self, mock_config_manager, article_store_with_corpus, sample_articles):
        """Flask test client with mocked SemanticRetriever."""
        from app.api import create_app

        mock_semantic = _make_mock_semantic_retriever(sample_articles)

        with patch("app.api.SemanticRetriever", return_value=mock_semantic):
            flask_app = create_app(
                config_manager=mock_config_manager,
                article_store=article_store_with_corpus,
            )

        return flask_app.test_client()

    def test_feedback_round_trip(self, feedback_client):
        """Submit a rating then retrieve it; verify user_rating, rating_count, average_rating.

        Requirements: 12.2, 12.5
        """
        item_id = "test-item-round-trip-001"
        session_id = "session-abc-123"
        rating = 4

        # POST /feedback
        post_resp = feedback_client.post(
            "/feedback",
            json={
                "item_id": item_id,
                "query": "deep learning neural networks",
                "rating": rating,
                "session_id": session_id,
            },
            content_type="application/json",
        )
        assert post_resp.status_code == 200, (
            f"Expected 200 from POST /feedback, got {post_resp.status_code}: "
            f"{post_resp.get_json()}"
        )

        # GET /feedback/{item_id}
        get_resp = feedback_client.get(
            f"/feedback/{item_id}?session_id={session_id}"
        )
        assert get_resp.status_code == 200, (
            f"Expected 200 from GET /feedback/{item_id}, got {get_resp.status_code}"
        )

        data = get_resp.get_json()
        assert data["user_rating"] == rating, (
            f"Expected user_rating={rating}, got {data.get('user_rating')}"
        )
        assert data["rating_count"] >= 1, (
            f"Expected rating_count >= 1, got {data.get('rating_count')}"
        )
        assert isinstance(data["average_rating"], (int, float)), (
            f"Expected average_rating to be a number, got {data.get('average_rating')!r}"
        )

    def test_feedback_invalid_rating_returns_422(self, feedback_client):
        """Rating outside [1, 5] must return HTTP 422."""
        post_resp = feedback_client.post(
            "/feedback",
            json={
                "item_id": "some-item",
                "query": "some query",
                "rating": 6,
            },
            content_type="application/json",
        )
        assert post_resp.status_code == 422

    def test_feedback_missing_item_id_returns_422(self, feedback_client):
        """Missing item_id must return HTTP 422."""
        post_resp = feedback_client.post(
            "/feedback",
            json={
                "query": "some query",
                "rating": 3,
            },
            content_type="application/json",
        )
        assert post_resp.status_code == 422

    def test_get_feedback_unknown_item_returns_zero_count(self, feedback_client):
        """GET /feedback for an unknown item_id returns rating_count=0 without error."""
        get_resp = feedback_client.get("/feedback/unknown-item-xyz-999")
        assert get_resp.status_code == 200
        data = get_resp.get_json()
        assert data["rating_count"] == 0

    def test_feedback_upsert_updates_existing_rating(self, feedback_client):
        """Submitting a second rating for the same (item_id, session_id) updates the record."""
        item_id = "test-item-upsert-001"
        session_id = "session-upsert-abc"

        # First submission
        feedback_client.post(
            "/feedback",
            json={
                "item_id": item_id,
                "query": "machine learning",
                "rating": 3,
                "session_id": session_id,
            },
            content_type="application/json",
        )

        # Second submission (update)
        feedback_client.post(
            "/feedback",
            json={
                "item_id": item_id,
                "query": "machine learning",
                "rating": 5,
                "session_id": session_id,
            },
            content_type="application/json",
        )

        get_resp = feedback_client.get(
            f"/feedback/{item_id}?session_id={session_id}"
        )
        data = get_resp.get_json()

        # Should have exactly 1 record (upsert, not duplicate)
        assert data["rating_count"] == 1, (
            f"Expected rating_count=1 after upsert, got {data['rating_count']}"
        )
        assert data["user_rating"] == 5, (
            f"Expected updated user_rating=5, got {data['user_rating']}"
        )


# ---------------------------------------------------------------------------
# Test 3 & 4: ContentVerifier with real embedding model
# ---------------------------------------------------------------------------

# Check if the model is available in the local cache without downloading
def _embedding_model_available() -> bool:
    """Return True if the sentence-transformer model is cached locally."""
    try:
        from pathlib import Path

        # HuggingFace hub cache uses the pattern:
        # ~/.cache/huggingface/hub/models--<org>--<model-name>/
        hub_cache = Path.home() / ".cache" / "huggingface" / "hub"
        if hub_cache.exists():
            for item in hub_cache.iterdir():
                # Directory name format: models--sentence-transformers--paraphrase-multilingual-mpnet-base-v2
                if "paraphrase-multilingual-mpnet-base-v2" in item.name:
                    return True

        # Also check sentence-transformers legacy cache
        st_cache = Path.home() / ".cache" / "torch" / "sentence_transformers"
        if st_cache.exists():
            for item in st_cache.iterdir():
                if "paraphrase-multilingual-mpnet-base-v2" in item.name:
                    return True

        return False
    except Exception:
        return False


_SKIP_EMBEDDING = not _embedding_model_available()
_SKIP_REASON = (
    "Embedding model 'paraphrase-multilingual-mpnet-base-v2' not found in local cache. "
    "Run the app once to download the model, then re-run these tests."
)


@pytest.mark.skipif(_SKIP_EMBEDDING, reason=_SKIP_REASON)
class TestContentVerifierWithRealModel:
    """ContentVerifier integration tests using the real sentence-transformer model.

    These tests load the actual embedding model and do NOT mock it.
    They are skipped if the model is not cached locally.
    Requirements: 5b.9, 5b.11, 5b.12
    """

    @pytest.fixture(scope="class")
    def real_semantic_retriever(self, tmp_path_factory):
        """Load the real SemanticRetriever once per test class."""
        from app.retrievers.semantic import SemanticRetriever, SemanticRetrieverError

        tmpdir = tmp_path_factory.mktemp("semantic")
        store = ArticleStore(
            vector_store_path=str(tmpdir / "faiss.index"),
            metadata_db_path=str(tmpdir / "articles.db"),
        )
        cfg = AppConfig()
        try:
            return SemanticRetriever(store, cfg)
        except SemanticRetrieverError as exc:
            pytest.skip(f"Embedding model unavailable: {exc}")

    # ── Test 3: blocklisted domain excluded ──────────────────────────────────

    def test_blocklisted_domain_excluded(self, real_semantic_retriever):
        """A web resource whose URL domain is in domain_blocklist must be excluded.

        Requirements: 5b.9
        """
        from app.verifiers.content import ContentVerifier

        verifier = ContentVerifier(real_semantic_retriever)
        config = AppConfig(
            domain_blocklist=["spam-site.com"],
            min_web_score=0.0,
            mismatch_threshold=0.3,
        )

        query_embedding = real_semantic_retriever.encode("deep learning neural networks")

        blocked_resource = WebResourceRecommendation(
            resource_type="web",
            title="Deep Learning Tutorial",
            url="https://spam-site.com/deep-learning",
            snippet="A tutorial on deep learning.",
            web_score=0.9,
        )
        clean_resource = WebResourceRecommendation(
            resource_type="web",
            title="Neural Networks Overview",
            url="https://legit-site.com/neural-networks",
            snippet="An overview of neural network architectures.",
            web_score=0.8,
        )

        _, verified_web = verifier.verify(
            articles=[],
            web_resources=[blocked_resource, clean_resource],
            query_embedding=query_embedding,
            query_language="en",
            config=config,
        )

        urls = [r.url for r in verified_web]
        assert "https://spam-site.com/deep-learning" not in urls, (
            "Blocklisted domain must be excluded from results"
        )
        assert "https://legit-site.com/neural-networks" in urls, (
            "Non-blocklisted resource must remain in results"
        )

    def test_blocklisted_subdomain_excluded(self, real_semantic_retriever):
        """A subdomain of a blocklisted domain must also be excluded.

        Requirements: 5b.9
        """
        from app.verifiers.content import ContentVerifier

        verifier = ContentVerifier(real_semantic_retriever)
        config = AppConfig(
            domain_blocklist=["spam-site.com"],
            min_web_score=0.0,
            mismatch_threshold=0.3,
        )

        query_embedding = real_semantic_retriever.encode("machine learning")

        blocked_subdomain = WebResourceRecommendation(
            resource_type="web",
            title="ML Tutorial",
            url="https://sub.spam-site.com/ml",
            snippet="Machine learning tutorial.",
            web_score=0.8,
        )

        _, verified_web = verifier.verify(
            articles=[],
            web_resources=[blocked_subdomain],
            query_embedding=query_embedding,
            query_language="en",
            config=config,
        )

        assert len(verified_web) == 0, (
            "Subdomain of blocklisted domain must be excluded"
        )

    # ── Test 4: flagged item carries localized warning ────────────────────────

    def test_flagged_web_resource_carries_romanian_warning(self, real_semantic_retriever):
        """A mismatched web resource verified with query_language='ro' carries the Romanian warning.

        Requirements: 5b.11, 5b.12
        """
        from app.verifiers.content import ContentVerifier

        verifier = ContentVerifier(real_semantic_retriever)
        # Very low threshold to reliably trigger the warning
        config = AppConfig(
            domain_blocklist=[],
            mismatch_threshold=0.01,
            min_web_score=0.0,
        )

        query_embedding = real_semantic_retriever.encode("machine learning algorithms")

        # Title is highly relevant; snippet is completely unrelated (ancient history)
        mismatched_web = WebResourceRecommendation(
            resource_type="web",
            title="Machine learning algorithms and neural networks",
            url="https://example.com/ml",
            snippet=(
                "The history of ancient Rome spans many centuries. "
                "Julius Caesar was a famous Roman general and statesman."
            ),
            web_score=0.8,
        )

        _, verified_ro = verifier.verify(
            articles=[],
            web_resources=[mismatched_web],
            query_embedding=query_embedding,
            query_language="ro",
            config=config,
        )

        flagged = [r for r in verified_ro if r.quality_warning is not None]
        assert len(flagged) >= 1, (
            "Expected at least one item to be flagged with a quality warning "
            f"(mismatch_threshold={config.mismatch_threshold})."
        )
        for item in flagged:
            assert item.quality_warning == "⚠ Verificați conținutul", (
                f"Expected Romanian warning '⚠ Verificați conținutul', got {item.quality_warning!r}"
            )

    def test_flagged_web_resource_carries_english_warning(self, real_semantic_retriever):
        """A mismatched web resource verified with query_language='en' carries the English warning.

        Requirements: 5b.11, 5b.12
        """
        from app.verifiers.content import ContentVerifier

        verifier = ContentVerifier(real_semantic_retriever)
        config = AppConfig(
            domain_blocklist=[],
            mismatch_threshold=0.01,
            min_web_score=0.0,
        )

        query_embedding = real_semantic_retriever.encode("machine learning algorithms")

        mismatched_web = WebResourceRecommendation(
            resource_type="web",
            title="Machine learning algorithms and neural networks",
            url="https://example.com/ml-en",
            snippet=(
                "The history of ancient Rome spans many centuries. "
                "Julius Caesar was a famous Roman general and statesman."
            ),
            web_score=0.8,
        )

        _, verified_en = verifier.verify(
            articles=[],
            web_resources=[mismatched_web],
            query_embedding=query_embedding,
            query_language="en",
            config=config,
        )

        flagged = [r for r in verified_en if r.quality_warning is not None]
        assert len(flagged) >= 1, (
            "Expected at least one item to be flagged with a quality warning."
        )
        for item in flagged:
            assert item.quality_warning == "⚠ Verify content", (
                f"Expected English warning '⚠ Verify content', got {item.quality_warning!r}"
            )

    def test_flagged_article_carries_localized_warning(self, real_semantic_retriever):
        """A mismatched article carries the correct localized warning.

        Requirements: 5b.11, 5b.12
        """
        from app.verifiers.content import ContentVerifier

        verifier = ContentVerifier(real_semantic_retriever)
        config = AppConfig(
            domain_blocklist=[],
            mismatch_threshold=0.01,
            min_article_score=0.0,
        )

        query_embedding = real_semantic_retriever.encode("deep learning image classification")

        # Title is about deep learning; abstract is completely off-topic
        mismatched_article_ro = ArticleRecommendation(
            resource_type="article",
            title="Deep learning for image classification and recognition",
            abstract_snippet=(
                "The Roman Empire was one of the largest empires in ancient history. "
                "It was founded in 27 BC and lasted until 476 AD."
            ),
            score=0.8,
            item_id="test-article-ro-001",
        )

        verified_ro, _ = verifier.verify(
            articles=[mismatched_article_ro],
            web_resources=[],
            query_embedding=query_embedding,
            query_language="ro",
            config=config,
        )

        flagged_ro = [a for a in verified_ro if a.quality_warning is not None]
        assert len(flagged_ro) >= 1, "Expected article to be flagged with Romanian warning."
        for item in flagged_ro:
            assert item.quality_warning == "⚠ Verificați conținutul", (
                f"Expected Romanian warning, got {item.quality_warning!r}"
            )

        # English variant
        mismatched_article_en = ArticleRecommendation(
            resource_type="article",
            title="Deep learning for image classification and recognition",
            abstract_snippet=(
                "The Roman Empire was one of the largest empires in ancient history. "
                "It was founded in 27 BC and lasted until 476 AD."
            ),
            score=0.8,
            item_id="test-article-en-002",
        )

        verified_en, _ = verifier.verify(
            articles=[mismatched_article_en],
            web_resources=[],
            query_embedding=query_embedding,
            query_language="en",
            config=config,
        )

        flagged_en = [a for a in verified_en if a.quality_warning is not None]
        assert len(flagged_en) >= 1, "Expected article to be flagged with English warning."
        for item in flagged_en:
            assert item.quality_warning == "⚠ Verify content", (
                f"Expected English warning, got {item.quality_warning!r}"
            )

    def test_non_blocklisted_domain_passes_through(self, real_semantic_retriever):
        """A web resource from a non-blocklisted domain is not excluded.

        Requirements: 5b.9
        """
        from app.verifiers.content import ContentVerifier

        verifier = ContentVerifier(real_semantic_retriever)
        config = AppConfig(
            domain_blocklist=["spam-site.com"],
            min_web_score=0.0,
            mismatch_threshold=0.3,
        )

        query_embedding = real_semantic_retriever.encode("deep learning")

        # Title and snippet are both about deep learning -- no mismatch expected
        clean_resource = WebResourceRecommendation(
            resource_type="web",
            title="Deep learning fundamentals",
            url="https://trusted-source.edu/deep-learning",
            snippet="An introduction to deep learning and neural networks.",
            web_score=0.8,
        )

        _, verified_web = verifier.verify(
            articles=[],
            web_resources=[clean_resource],
            query_embedding=query_embedding,
            query_language="en",
            config=config,
        )

        assert len(verified_web) == 1, "Non-blocklisted resource should not be excluded"
        assert verified_web[0].url == "https://trusted-source.edu/deep-learning"
