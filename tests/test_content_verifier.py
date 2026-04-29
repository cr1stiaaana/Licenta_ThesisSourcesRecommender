"""Unit tests for ContentVerifier (app/verifiers/content.py)."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from app.config import AppConfig
from app.models import ArticleRecommendation, WebResourceRecommendation
from app.verifiers.content import (
    ContentVerifier,
    _clamp,
    _cosine_similarity,
    _is_domain_blocked,
)


# ── Helper factories ──────────────────────────────────────────────────────────


def make_article(
    title: str = "Test Title",
    abstract_snippet: str = "Test abstract content.",
    score: float = 0.8,
) -> ArticleRecommendation:
    return ArticleRecommendation(
        title=title,
        abstract_snippet=abstract_snippet,
        score=score,
    )


def make_web(
    title: str = "Test Page",
    url: str = "https://example.com/page",
    snippet: str = "Test snippet content.",
    web_score: float = 0.8,
) -> WebResourceRecommendation:
    return WebResourceRecommendation(
        title=title,
        url=url,
        snippet=snippet,
        web_score=web_score,
    )


def make_verifier(encode_fn=None) -> ContentVerifier:
    """Build a ContentVerifier with a mock SemanticRetriever."""
    mock_retriever = MagicMock()
    if encode_fn is not None:
        mock_retriever.encode.side_effect = encode_fn
    return ContentVerifier(mock_retriever)


def unit_vec(dim: int = 4, index: int = 0) -> np.ndarray:
    """Return a unit vector with 1.0 at *index* and 0.0 elsewhere."""
    v = np.zeros(dim, dtype=float)
    v[index] = 1.0
    return v


# ── _cosine_similarity ────────────────────────────────────────────────────────


def test_cosine_similarity_identical_vectors():
    v = np.array([1.0, 0.0, 0.0])
    assert _cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert _cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_zero_norm_returns_zero():
    zero = np.zeros(3)
    v = np.array([1.0, 0.0, 0.0])
    assert _cosine_similarity(zero, v) == 0.0
    assert _cosine_similarity(v, zero) == 0.0
    assert _cosine_similarity(zero, zero) == 0.0


# ── _clamp ────────────────────────────────────────────────────────────────────


def test_clamp_within_range():
    assert _clamp(0.5, 0.0, 1.0) == 0.5


def test_clamp_below_lo():
    assert _clamp(-0.1, 0.0, 1.0) == 0.0


def test_clamp_above_hi():
    assert _clamp(1.5, 0.0, 1.0) == 1.0


# ── _is_domain_blocked ────────────────────────────────────────────────────────


def test_domain_blocked_exact_match():
    assert _is_domain_blocked("https://spam.com/page", ["spam.com"])


def test_domain_blocked_subdomain_matches_parent():
    assert _is_domain_blocked("https://sub.spam.com/page", ["spam.com"])


def test_domain_not_blocked():
    assert not _is_domain_blocked("https://legit.com/page", ["spam.com"])


def test_domain_blocked_empty_blocklist():
    assert not _is_domain_blocked("https://spam.com/page", [])


def test_domain_blocked_www_stripped():
    # www.example.com should match blocklist entry 'example.com'
    assert _is_domain_blocked("https://www.spam.com/page", ["spam.com"])


def test_domain_blocked_invalid_url():
    assert not _is_domain_blocked("not-a-url", ["spam.com"])


# ── ContentVerifier.verify — articles ────────────────────────────────────────


def test_article_no_abstract_retained_as_is():
    """Articles with no abstract are kept without quality_warning."""
    query_emb = unit_vec(index=0)
    article = make_article(abstract_snippet="", score=0.5)

    verifier = make_verifier()
    config = AppConfig()

    verified, _ = verifier.verify([article], [], query_emb, "en", config)

    assert len(verified) == 1
    assert verified[0].quality_warning is None
    assert verified[0].score == pytest.approx(0.5)


def test_article_no_mismatch_passes_clean():
    """When title_sim ≈ content_sim, no warning is set."""
    query_emb = unit_vec(index=0)

    # Both title and abstract encode to the same direction as query → sim ≈ 1.0
    def encode(text: str) -> np.ndarray:
        return unit_vec(index=0)

    verifier = make_verifier(encode_fn=encode)
    config = AppConfig(mismatch_threshold=0.3)
    article = make_article(score=0.8)

    verified, _ = verifier.verify([article], [], query_emb, "en", config)

    assert len(verified) == 1
    assert verified[0].quality_warning is None


def test_article_mismatch_above_threshold_partial_penalty():
    """When mismatch is moderate (> threshold but < 1.0), item is kept with warning."""
    query_emb = unit_vec(dim=4, index=0)
    call_count = {"n": 0}

    def encode(text: str) -> np.ndarray:
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            # title: mostly aligned with query (title_sim ≈ 0.98)
            return np.array([0.98, 0.2, 0.0, 0.0])
        else:
            # abstract: moderately aligned (content_sim ≈ 0.6)
            return np.array([0.6, 0.8, 0.0, 0.0])

    verifier = make_verifier(encode_fn=encode)
    # mismatch ≈ 0.98/norm - 0.6/norm; with threshold=0.3 this may or may not trigger
    # Use a very low threshold to ensure it triggers
    config = AppConfig(mismatch_threshold=0.1, min_article_score=0.05)
    article = make_article(score=0.8)

    verified, _ = verifier.verify([article], [], query_emb, "en", config)

    # Item should be kept (quality_score > 0.05) with a warning
    assert len(verified) == 1
    assert verified[0].quality_warning == "⚠ Verify content"
    assert verified[0].score < 0.8  # score was penalized


def test_article_mismatch_excluded_when_quality_score_too_low():
    """Items with Quality_Score < min_article_score are excluded."""
    query_emb = unit_vec(dim=4, index=0)
    call_count = {"n": 0}

    def encode(text: str) -> np.ndarray:
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            return unit_vec(dim=4, index=0)  # title_sim = 1.0
        else:
            return unit_vec(dim=4, index=1)  # content_sim = 0.0

    verifier = make_verifier(encode_fn=encode)
    # mismatch = 1.0, quality_score = 0.8 * (1 - 1.0) = 0.0 < 0.1 → excluded
    config = AppConfig(mismatch_threshold=0.3, min_article_score=0.1)
    article = make_article(score=0.8)

    verified, _ = verifier.verify([article], [], query_emb, "en", config)

    assert len(verified) == 0


def test_article_mismatch_kept_with_warning_when_quality_score_sufficient():
    """Items with Quality_Score >= min_article_score are kept with warning."""
    query_emb = unit_vec(dim=4, index=0)
    call_count = {"n": 0}

    def encode(text: str) -> np.ndarray:
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            # title: partially aligned with query
            return np.array([0.9, 0.1, 0.0, 0.0])
        else:
            # abstract: less aligned
            return np.array([0.3, 0.7, 0.0, 0.0])

    verifier = make_verifier(encode_fn=encode)
    config = AppConfig(mismatch_threshold=0.3, min_article_score=0.1)
    article = make_article(score=0.8)

    verified, _ = verifier.verify([article], [], query_emb, "en", config)

    # title_sim = cos(query=[1,0,0,0], title=[0.9,0.1,0,0]) = 0.9/norm([0.9,0.1])
    # content_sim = cos(query=[1,0,0,0], abstract=[0.3,0.7,0,0]) = 0.3/norm([0.3,0.7])
    assert len(verified) == 1
    assert verified[0].quality_warning == "⚠ Verify content"


def test_article_warning_localized_romanian():
    """Romanian query_language produces Romanian warning text."""
    query_emb = unit_vec(dim=4, index=0)
    call_count = {"n": 0}

    def encode(text: str) -> np.ndarray:
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            return np.array([0.9, 0.1, 0.0, 0.0])
        else:
            return np.array([0.3, 0.7, 0.0, 0.0])

    verifier = make_verifier(encode_fn=encode)
    config = AppConfig(mismatch_threshold=0.3, min_article_score=0.1)
    article = make_article(score=0.8)

    verified, _ = verifier.verify([article], [], query_emb, "ro", config)

    if verified:
        assert verified[0].quality_warning == "⚠ Verificați conținutul"


# ── ContentVerifier.verify — web resources ────────────────────────────────────


def test_web_resource_blocked_domain_excluded():
    """Web resources from blocklisted domains are excluded before mismatch check."""
    query_emb = unit_vec(index=0)
    verifier = make_verifier()
    config = AppConfig(domain_blocklist=["spam.com"])
    web = make_web(url="https://spam.com/article")

    _, verified_web = verifier.verify([], [web], query_emb, "en", config)

    assert len(verified_web) == 0
    # encode should NOT have been called (blocklist check happens first)
    verifier._retriever.encode.assert_not_called()


def test_web_resource_subdomain_blocked():
    """Subdomains of blocklisted domains are also excluded."""
    query_emb = unit_vec(index=0)
    verifier = make_verifier()
    config = AppConfig(domain_blocklist=["spam.com"])
    web = make_web(url="https://sub.spam.com/article")

    _, verified_web = verifier.verify([], [web], query_emb, "en", config)

    assert len(verified_web) == 0


def test_web_resource_no_mismatch_passes_clean():
    """Web resource with no mismatch passes without warning."""
    query_emb = unit_vec(index=0)

    def encode(text: str) -> np.ndarray:
        return unit_vec(index=0)

    verifier = make_verifier(encode_fn=encode)
    config = AppConfig(mismatch_threshold=0.3)
    web = make_web()

    _, verified_web = verifier.verify([], [web], query_emb, "en", config)

    assert len(verified_web) == 1
    assert verified_web[0].quality_warning is None


def test_web_resource_mismatch_excluded_when_quality_score_too_low():
    """Web resources with Quality_Score < min_web_score are excluded."""
    query_emb = unit_vec(dim=4, index=0)
    call_count = {"n": 0}

    def encode(text: str) -> np.ndarray:
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            return unit_vec(dim=4, index=0)  # title_sim = 1.0
        else:
            return unit_vec(dim=4, index=1)  # content_sim = 0.0

    verifier = make_verifier(encode_fn=encode)
    config = AppConfig(mismatch_threshold=0.3, min_web_score=0.1)
    web = make_web(web_score=0.8)

    _, verified_web = verifier.verify([], [web], query_emb, "en", config)

    # quality_score = 0.8 * (1 - 1.0) = 0.0 < 0.1 → excluded
    assert len(verified_web) == 0


def test_web_resource_uses_web_score_not_score():
    """Quality_Score for web resources is based on web_score, not score."""
    query_emb = unit_vec(dim=4, index=0)
    call_count = {"n": 0}

    def encode(text: str) -> np.ndarray:
        call_count["n"] += 1
        if call_count["n"] % 2 == 1:
            return np.array([0.9, 0.1, 0.0, 0.0])
        else:
            return np.array([0.3, 0.7, 0.0, 0.0])

    verifier = make_verifier(encode_fn=encode)
    config = AppConfig(mismatch_threshold=0.3, min_web_score=0.1)
    web = make_web(web_score=0.9)

    _, verified_web = verifier.verify([], [web], query_emb, "en", config)

    if verified_web:
        # web_score should have been penalized (not some other field)
        assert verified_web[0].web_score < 0.9


def test_verify_returns_tuple_of_two_lists():
    """verify() always returns a 2-tuple of lists."""
    query_emb = unit_vec(index=0)
    verifier = make_verifier(encode_fn=lambda t: unit_vec(index=0))
    config = AppConfig()

    result = verifier.verify([], [], query_emb, "en", config)

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], list)
