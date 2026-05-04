# Technology Stack

## Backend

- **Framework**: Flask 3.1.1
- **Language**: Python 3.10+
- **Search & Retrieval**:
  - FAISS (faiss-cpu 1.10.0) for semantic vector search
  - BM25 (rank_bm25 0.2.2) for keyword matching
  - sentence-transformers 3.4.1 with `paraphrase-multilingual-mpnet-base-v2` model
- **Database**: SQLite (articles, feedback, users)
- **Language Detection**: langdetect 1.0.9, langid 1.1.6
- **Testing**: pytest 8.3.5, hypothesis 6.131.15 (property-based testing)
- **Configuration**: PyYAML 6.0.2 with hot-reload via watchdog 6.0.0
- **Web Search**: ddgs 9.14.1 (DuckDuckGo), requests 2.32.3

## Frontend

- Vanilla JavaScript (no framework)
- HTML5 + CSS3
- Dark mode support

## Common Commands

### Development

```bash
# Start the development server (default: http://localhost:5000)
python app/main.py

# Start with custom host/port
python app/main.py serve --host 0.0.0.0 --port 8080

# Enable debug mode
python app/main.py serve --debug
```

### Data Management

```bash
# Add sample articles to the database
python add_realistic_articles.py
python add_spec_articles.py
python add_test_articles.py

# Populate article store
python populate_article_store.py

# Build/rebuild search indexes
python build_indexes.py
python rebuild_indexes.py
```

### Ingestion

```bash
# Ingest articles from various formats
python app/main.py ingest --file data/articles.json --format json
python app/main.py ingest --file data/articles.csv --format csv
python app/main.py ingest --file data/refs.bib --format bibtex
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_integration.py

# Run with verbose output
pytest -v

# Run specific test class or method
pytest tests/test_integration.py::TestRecommendEndToEnd::test_response_structure
```

### Testing Individual Components

```bash
# Test retrievers
python test_retrievers.py
python test_retrievers_fixed.py

# Test web search
python test_web_search.py
python test_academic_search.py

# Test full system
python test_full_system.py
python test_recommend_endpoint.py

# Debug hybrid ranker
python debug_hybrid_ranker.py
```

## Configuration

- **Main config**: `config.yaml` (hot-reloadable)
- **Database config**: `database_config.env.example` (template)
- Edit `config.yaml` to tune:
  - Retrieval weights (semantic vs keyword)
  - Top-K limits
  - Score thresholds
  - Web search provider
  - Timeouts
  - Content quality filters
  - Feedback settings

## Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

The embedding model (`paraphrase-multilingual-mpnet-base-v2`) will be downloaded automatically on first run.
