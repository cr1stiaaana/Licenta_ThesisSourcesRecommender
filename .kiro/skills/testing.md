---
name: testing
description: Ghid complet pentru scrierea și rularea testelor (pytest, hypothesis, integration tests).
version: 1.0.0
---

# Skill: Testing Strategy

## Overview

This skill guides writing and running tests for the Hybrid Thesis Recommender.

## Test Structure

```
tests/
├── test_integration.py         # End-to-end API tests
├── test_content_verifier.py    # Content quality verification
├── test_full_system.py         # Full system with real models
├── test_retrievers.py          # Retriever unit tests
└── test_web_search.py          # Web search adapter tests
```

## Running Tests

```bash
# All tests (fast, skips model-dependent)
pytest tests/ -v --tb=short

# Specific file
pytest tests/test_integration.py -v

# Specific test class
pytest tests/test_integration.py::TestRecommendEndToEnd -v

# Specific test method
pytest tests/test_integration.py::TestRecommendEndToEnd::test_response_structure -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Property-based tests only
pytest tests/ -v -k "hypothesis"
```

## Test Categories

### Unit Tests
Test individual components in isolation with mocked dependencies:
- `SemanticRetriever` with mocked FAISS index
- `KeywordRetriever` with mocked BM25
- `ContentVerifier` with mocked embeddings
- `FeedbackStore` with temp SQLite DB
- `HybridRanker` with known inputs

### Integration Tests
Test full request/response cycle:
- `POST /recommend` → validate response structure
- `POST /feedback` → `GET /feedback/{id}` round-trip
- Error handling (invalid input, component failures)

### Property-Based Tests (Hypothesis)
Test invariants that must hold for ALL inputs:
- Scores always in [0.0, 1.0]
- Quality warning set iff mismatch > threshold
- Blocklisted domains never in output
- Upsert idempotence (same item_id → one record)

## Writing a New Test

### Template: Unit Test
```python
import pytest
from unittest.mock import MagicMock, patch
from app.retrievers.semantic import SemanticRetriever

class TestSemanticRetriever:
    @pytest.fixture
    def mock_model(self):
        model = MagicMock()
        model.encode.return_value = [[0.1] * 768]
        return model
    
    def test_scores_normalized(self, mock_model):
        retriever = SemanticRetriever(model=mock_model, index=mock_index)
        result = retriever.retrieve(query, top_k=5)
        for article in result.articles:
            assert 0.0 <= article.score <= 1.0
```

### Template: Property Test
```python
from hypothesis import given, strategies as st

@given(
    title_sim=st.floats(min_value=0, max_value=1),
    content_sim=st.floats(min_value=0, max_value=1),
    threshold=st.floats(min_value=0, max_value=1),
)
def test_quality_warning_correctness(title_sim, content_sim, threshold):
    mismatch = title_sim - content_sim
    should_flag = mismatch > threshold
    # ... verify ContentVerifier behavior matches
```

## Fixtures

### Common Fixtures
- `tmp_db`: Temporary SQLite database (auto-cleaned)
- `mock_config`: AppConfig with test defaults
- `sample_articles`: List of 10 test articles with embeddings
- `flask_client`: Flask test client with mocked components

## CI Integration

Tests run automatically in GitHub Actions on push/PR:
```yaml
- name: Run pytest
  run: pytest tests/ -v --tb=short --ignore=tests/test_full_system.py
```

Note: `test_full_system.py` is ignored in CI because it requires the embedding model downloaded (~420MB).
