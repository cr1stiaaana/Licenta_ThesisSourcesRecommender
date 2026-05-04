# Project Structure

## Directory Layout

```
├── app/                      # Main application package
│   ├── auth/                 # User authentication & saved items
│   ├── feedback/             # Rating/feedback storage
│   ├── ingestion/            # Article ingestion pipeline
│   ├── rankers/              # Hybrid ranking (RRF, weighted sum)
│   ├── retrievers/           # Semantic, keyword, web, academic retrievers
│   ├── verifiers/            # Content quality verification
│   ├── web_search/           # Web search adapters (DuckDuckGo, Google, Bing)
│   ├── api.py                # Flask REST API & blueprints
│   ├── article_store.py      # FAISS + SQLite storage layer
│   ├── config.py             # AppConfig dataclass
│   ├── config_manager.py     # Hot-reloadable config with watchdog
│   ├── i18n.py               # Internationalization (ro/en)
│   ├── language_detector.py  # Query language detection
│   ├── main.py               # Entry point (serve, ingest commands)
│   └── models.py             # Data models (Article, Query, etc.)
├── static/                   # Frontend assets
│   ├── index.html            # Main UI
│   ├── app.js                # Client-side logic
│   └── style.css             # Styles with dark mode
├── tests/                    # Test suite
│   ├── test_integration.py   # End-to-end API tests
│   └── test_content_verifier.py
├── data/                     # Runtime data (SQLite DBs, indexes)
│   ├── articles.db           # Article metadata
│   ├── faiss.index           # Vector embeddings
│   ├── bm25.pkl              # BM25 index
│   ├── feedback.db           # User ratings
│   └── users.db              # User accounts & saved items
├── database/                 # Database schemas
│   └── schema.sql
├── config.yaml               # Main configuration file
└── requirements.txt          # Python dependencies
```

## Architecture Patterns

### Component Organization

- **Modular design**: Each major feature (auth, feedback, retrievers, rankers, verifiers) is in its own module
- **Dependency injection**: Components are instantiated in `api.py` and passed to blueprints
- **Application factory**: `create_app(config_manager, article_store)` for testability

### Data Flow

1. **Query** → Language detection → Parallel retrieval (semantic, keyword, academic, web)
2. **Retrieval results** → Hybrid ranker (RRF or weighted sum fusion)
3. **Ranked results** → Content verifier (quality checks, domain blocklist)
4. **Response** → JSON serialization with localized messages

### Storage Layer

- **ArticleStore**: Unified interface for FAISS (vectors) + SQLite (metadata)
- **FeedbackStore**: SQLite-based rating persistence with upsert semantics
- **UserStore**: SQLite-based user accounts and saved items

### Configuration

- **AppConfig dataclass**: Type-safe configuration with defaults
- **ConfigManager**: Watches `config.yaml` for changes and hot-reloads
- **No restart required**: Config changes apply to new requests immediately

### API Structure

- **Blueprint-based**: Separate blueprints for recommend, feedback, auth
- **Graceful degradation**: If semantic or keyword retriever fails, system continues with available retrievers
- **Timeout handling**: Parallel execution with configurable timeouts per component

## Code Conventions

### Python Style

- **Type hints**: Use `from __future__ import annotations` and type all function signatures
- **Dataclasses**: Prefer dataclasses for data models (see `models.py`)
- **Docstrings**: Module-level docstrings list requirements; function docstrings explain purpose
- **Error handling**: Custom exception classes (e.g., `SemanticRetrieverError`, `FeedbackStoreError`)
- **Logging**: Use `logging` module with appropriate levels (INFO, WARNING, ERROR)

### Testing

- **pytest fixtures**: Shared fixtures in test files for temp directories, mock components
- **Integration tests**: Test full request/response cycle with mocked external dependencies
- **Property-based testing**: Use Hypothesis for testing invariants (see requirements)
- **Model caching**: Tests skip if embedding model not cached locally (avoid CI downloads)

### Naming Conventions

- **Files**: Snake case (e.g., `article_store.py`, `hybrid_ranker.py`)
- **Classes**: PascalCase (e.g., `ArticleStore`, `HybridRanker`)
- **Functions/variables**: Snake case (e.g., `get_ratings`, `query_language`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `_EMBEDDING_DIM`)
- **Private helpers**: Leading underscore (e.g., `_validate_title`, `_serialize_response`)

### Import Organization

1. Standard library imports
2. Third-party imports
3. Local application imports
4. Use `from __future__ import annotations` at the top

### Error Messages

- **Localized**: Use `i18n.t(key, language)` for user-facing messages
- **Bilingual**: Support both Romanian ("ro") and English ("en")
- **Quality warnings**: Localized emoji warnings (⚠ Verificați conținutul / ⚠ Verify content)

## Key Files

- **app/main.py**: Entry point with CLI (serve, ingest)
- **app/api.py**: Flask app factory and all route handlers
- **app/models.py**: All data models as dataclasses
- **app/config.py**: Configuration schema
- **config.yaml**: Runtime configuration (edit this, not code)
- **tests/test_integration.py**: Comprehensive integration test suite
