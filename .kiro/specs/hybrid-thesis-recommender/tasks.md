# Implementation Plan: Hybrid Thesis Recommender

## Overview

Implement the Hybrid Thesis Recommender as a Flask application with a multilingual hybrid retrieval pipeline (semantic + BM25 + live web search), a plain HTML/CSS/JS frontend, and a SQLite-backed feedback store. Tasks are ordered so each step builds on the previous one, ending with full integration and wiring.

## Tasks

- [x] 1. Project scaffold and configuration layer
  - Create the directory structure: `app/`, `app/retrievers/`, `app/rankers/`, `app/verifiers/`, `app/ingestion/`, `app/feedback/`, `app/web_search/`, `static/`, `data/`, `tests/`
  - Create `requirements.txt` pinning: `flask`, `sentence-transformers`, `faiss-cpu`, `rank_bm25`, `langdetect`, `langid`, `watchdog`, `PyYAML`, `bibtexparser`, `hypothesis`, `pytest`
  - Implement `app/config.py`: define `AppConfig` dataclass with all fields from the design (retrieval weights, top-k values, score thresholds, embedding model, vector store paths, web search settings, language options, timeouts, mismatch threshold, domain blocklist, feedback settings)
  - Implement `app/config_manager.py`: `ConfigManager` class that reads a YAML config file, validates all fields (rejects negative weights, zero top-k, unknown fusion strategies), retains previous valid config on error, and uses `watchdog` to hot-reload on file change
  - Write `config.yaml` with default values matching `AppConfig` defaults
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 2. Data models
  - [x] 2.1 Implement all dataclasses in `app/models.py`
    - Define `Article`, `Query` (with `combined_text()` method), `RetrievalResult`, `ScoredArticle`, `WebRetrievalResult`, `RawWebResult`, `ArticleRecommendation`, `WebResourceRecommendation`, `RecommendResponse`, `FeedbackEntry`, `FeedbackRequest`, `FeedbackResponse`, `FeedbackQueryResult`
    - _Requirements: 1.1, 1.2, 1.3, 5.1, 5.2, 12.1_

- [ ] 3. Language detection
  - [x] 3.1 Implement `app/language_detector.py`: `LanguageDetector` class
    - Use `langdetect` and `langid` ensemble: return the agreed result; default to `"en"` when they disagree or either raises an exception
    - _Requirements: 1.6, 1.7, 10.2_

  - [ ]* 3.2 Write unit tests for `LanguageDetector`
    - Test correct detection for clear Romanian and English samples
    - Test fallback to `"en"` on ambiguous or very short input
    - Test fallback to `"en"` when both libraries raise exceptions
    - _Requirements: 1.6, 1.7_

- [x] 4. Article store and ingestion pipeline
  - [x] 4.1 Implement `app/article_store.py`: `ArticleStore` class
    - Initialize a FAISS flat index (L2 or inner-product) for 768-dimensional embeddings
    - Initialize a SQLite metadata database at `metadata_db_path` with schema: `articles(id TEXT PRIMARY KEY, title TEXT, abstract TEXT, authors TEXT, year INTEGER, doi TEXT, url TEXT, keywords TEXT, language TEXT)`
    - Implement `add_article(article, embedding)` with upsert semantics (by `article.id`)
    - Implement `get_all_texts()` returning tokenized corpus for BM25 index construction
    - Implement `search_vector(query_embedding, top_k)` returning `list[ScoredArticle]`
    - Implement `get_article_by_id(id)` for metadata lookup
    - _Requirements: 7.2, 7.3, 7.5_

  - [x] 4.2 Implement `app/ingestion/pipeline.py`: `IngestionPipeline` class
    - Implement `ingest_file(path, format)` supporting `"json"`, `"csv"`, and `"bibtex"` formats
    - For each valid article: generate embedding using the configured model, compute `article.id` as SHA-256 of DOI (preferred) or normalized title, detect article language with `LanguageDetector`, upsert into `ArticleStore`
    - Skip articles missing `title` or `abstract` and log a warning with the record identifier
    - Return an `IngestionReport` with counts of ingested, skipped, and failed records
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [ ]* 4.3 Write unit tests for `IngestionPipeline`
    - Test JSON, CSV, and BibTeX parsing with valid records
    - Test that records missing title or abstract are skipped and logged
    - Test incremental upsert (same DOI ingested twice results in one record)
    - _Requirements: 7.1, 7.4, 7.5_

- [x] 5. Semantic retriever
  - [x] 5.1 Implement `app/retrievers/semantic.py`: `SemanticRetriever` class
    - Load `paraphrase-multilingual-mpnet-base-v2` once at startup using `sentence_transformers.SentenceTransformer`; cache the model instance
    - Implement `retrieve(query, top_k)`: encode `query.combined_text()`, search the FAISS index, normalize cosine scores to `[0.0, 1.0]` via `(score + 1) / 2`, return `RetrievalResult` with `source="semantic"`
    - Raise `SemanticRetrieverError` on model or index failure
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 10.3, 10.4, 10.5_

  - [ ]* 5.2 Write unit tests for `SemanticRetriever`
    - Test that scores are normalized to `[0.0, 1.0]`
    - Test that `SemanticRetrieverError` is raised when the model is unavailable (mock the model)
    - _Requirements: 2.4, 2.5_

- [x] 6. Keyword retriever
  - [x] 6.1 Implement `app/retrievers/keyword.py`: `KeywordRetriever` class
    - Build a `rank_bm25.BM25Okapi` index from the article corpus at startup; persist/load the index from `bm25_index_path` using `pickle`
    - Implement `retrieve(query, top_k)`: tokenize `query.combined_text()` by whitespace and punctuation, run BM25, normalize scores by dividing by the max score (or `1.0` if all scores are zero), return `RetrievalResult` with `source="keyword"`
    - Return an empty `RetrievalResult` (no error) when no terms match
    - Raise `KeywordRetrieverError` on index failure
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 10.6_

  - [ ]* 6.2 Write unit tests for `KeywordRetriever`
    - Test BM25 score normalization to `[0.0, 1.0]`
    - Test empty result returned (not an error) when no terms match
    - Test `KeywordRetrieverError` raised on index failure (mock the index)
    - _Requirements: 3.3, 3.4_

- [x] 7. Checkpoint — core retrievers working
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Web retriever and search adapters
  - [x] 8.1 Implement `app/web_search/base.py`: abstract `WebSearchAdapter` with `search(query, num_results) -> list[RawWebResult]`
  - [x] 8.2 Implement `app/web_search/duckduckgo.py`: `DuckDuckGoAdapter`
    - Implement `search()` using the DuckDuckGo search API; map results to `RawWebResult` with rank-based `web_score = 1.0 / (rank + 1)` (normalized over the result set)
    - _Requirements: 6.3, 6.4_

  - [x] 8.3 Implement `app/web_search/google_cse.py`: `GoogleCSEAdapter` and `app/web_search/bing.py`: `BingSearchAdapter`
    - Both implement the same `WebSearchAdapter` interface; credentials read from `AppConfig`
    - _Requirements: 6.9_

  - [x] 8.4 Implement `app/retrievers/web.py`: `WebRetriever` class
    - Select the adapter based on `AppConfig.web_search_provider`
    - Implement `retrieve(query, query_language)`: issue search in `query_language`; if `bilingual_web_search` is enabled, issue parallel queries in both `"ro"` and `"en"` and merge results deduplicating by URL
    - Filter out URLs that return HTTP 4xx/5xx on a lightweight HEAD request
    - Return empty `WebRetrievalResult` (no error) when the API is unavailable
    - _Requirements: 6.1, 6.2, 6.5, 6.6, 6.7, 6.8, 6.10_

  - [ ]* 8.5 Write unit tests for `WebRetriever`
    - Test URL deduplication in bilingual mode
    - Test that inaccessible URLs (mocked HTTP errors) are filtered out
    - Test that an empty result is returned (not an error) when the adapter raises
    - _Requirements: 6.5, 6.8, 6.10_

- [x] 9. Hybrid ranker
  - [x] 9.1 Implement `app/rankers/hybrid.py`: `HybridRanker` class
    - Implement `fuse_articles(semantic, keyword, top_k, semantic_weight, keyword_weight)`:
      - Default strategy: RRF — `RRF_score(d) = Σ_r weight_r / (60 + rank_r(d))`
      - Alternative strategy: weighted score sum (selected via `AppConfig.fusion_strategy`)
      - Deduplicate by DOI (preferred) or normalized title
      - Apply feedback signal boost when `feedback_signal_enabled=True`: `boosted = rrf_score + boost * (avg_rating - 1) / 4` for items with `avg_rating >= feedback_signal_min_rating`
      - Apply `min_article_score` threshold; return top-k ordered by descending score
    - Implement `rank_web_resources(web, top_k)`: apply `min_web_score` threshold, return top-k ordered by descending `web_score`
    - Attach `resource_type` label to every item
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 5.4, 5.7, 5.8, 5.10, 12.8, 12.9_

  - [ ]* 9.2 Write unit tests for `HybridRanker`
    - Test RRF formula with known inputs and expected scores
    - Test deduplication by DOI and by normalized title
    - Test single-retriever fallback (one result set empty)
    - Test feedback boost applied when enabled and not applied when disabled
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 12.8, 12.9_

- [x] 10. Content verifier
  - [x] 10.1 Implement `app/verifiers/content.py`: `ContentVerifier` class
    - Implement `verify(articles, web_resources, query_embedding, query_language, config)`:
      - For each article with a non-empty abstract: compute `title_sim` and `content_sim` using the same multilingual embedding model; if `(title_sim - content_sim) > mismatch_threshold`, compute `Quality_Score = score * (1 - clamp(title_sim - content_sim, 0, 1))`, set `quality_warning` to the localized string; exclude items whose `Quality_Score < min_article_score`
      - For articles with no abstract: retain as-is without `quality_warning`
      - For each web resource: check domain against `domain_blocklist` first (exclude if matched); then apply the same mismatch check using the snippet; exclude items whose `Quality_Score < min_web_score`
      - Localized warnings: `"⚠ Verificați conținutul"` (ro) / `"⚠ Verify content"` (en)
      - Make NO HTTP requests during evaluation
    - _Requirements: 5b.1, 5b.2, 5b.3, 5b.4, 5b.5, 5b.6, 5b.7, 5b.8, 5b.9, 5b.10, 5b.11, 5b.12_

  - [ ]* 10.2 Write property test for ContentVerifier flagging correctness
    - **Property 1: ContentVerifier flagging correctness**
    - Generate random `(title_sim, content_sim, threshold)` floats in `[0, 1]`; verify `quality_warning` is set if and only if `(title_sim - content_sim) > threshold`
    - **Validates: Requirements 5b.3**

  - [ ]* 10.3 Write property test for ContentVerifier filter completeness
    - **Property 2: ContentVerifier filter completeness**
    - Generate random item lists with random `Quality_Score` values; verify no output item has a score below the applicable minimum threshold; verify flagged items above threshold carry `quality_warning`
    - **Validates: Requirements 5b.5, 5b.6**

  - [ ]* 10.4 Write property test for articles without abstracts passing through unflagged
    - **Property 3: Articles without abstracts pass through unflagged**
    - Generate articles with `abstract=None` or `abstract=""`; verify all are retained in output without `quality_warning`, regardless of threshold
    - **Validates: Requirements 5b.8**

  - [ ]* 10.5 Write property test for domain blocklist exclusion
    - **Property 4: Domain blocklist exclusion**
    - Generate random URLs and domain blocklists; verify every web resource whose registered domain is in the blocklist is absent from the output
    - **Validates: Requirements 5b.9**

  - [ ]* 10.6 Write unit tests for `ContentVerifier`
    - Test localized warning strings for `"ro"` and `"en"` query languages
    - Test that no HTTP requests are made during evaluation (mock the embedding model)
    - Test domain blocklist matching including subdomain-to-parent matching
    - _Requirements: 5b.7, 5b.9, 5b.11, 5b.12_

- [x] 11. Checkpoint — retrieval and ranking pipeline complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Feedback store
  - [x] 12.1 Implement `app/feedback/store.py`: `FeedbackStore` class
    - Initialize SQLite database at `feedback_store_path`; create table `ratings(item_id TEXT, session_id TEXT, query TEXT, rating INTEGER, updated_at TIMESTAMP, UNIQUE(item_id, session_id))`
    - Implement `upsert_rating(item_id, query, rating, session_id, timestamp)` using `INSERT OR REPLACE`
    - Implement `get_ratings(item_id, session_id)` returning `FeedbackQueryResult` with `user_rating`, `average_rating`, and `rating_count`; return zero-count result without error when no ratings exist
    - Raise `FeedbackStoreError` when the database is unavailable
    - _Requirements: 12.2, 12.4, 12.5, 12.6, 12.7, 12.11_

  - [ ]* 12.2 Write property test for rating persistence round-trip
    - **Property 5: Rating persistence round-trip**
    - Generate valid `(item_id, query, rating, session_id)` tuples; submit via `upsert_rating`, then call `get_ratings`; verify `user_rating` equals submitted rating and `rating_count >= 1`
    - **Validates: Requirements 12.2, 12.7**

  - [ ]* 12.3 Write property test for rating validation rejects out-of-range values
    - **Property 6: Rating validation rejects out-of-range values**
    - Generate rating values outside `[1, 5]`; verify the API returns HTTP 422 and no record is persisted in `FeedbackStore`
    - **Validates: Requirements 12.3**

  - [ ]* 12.4 Write property test for rating upsert idempotence
    - **Property 7: Rating upsert idempotence**
    - Generate sequences of N ratings for the same `(item_id, session_id)` pair; verify exactly one record exists in `FeedbackStore` after all submissions, containing the most recently submitted rating
    - **Validates: Requirements 12.4**

  - [ ]* 12.5 Write unit tests for `FeedbackStore`
    - Test upsert semantics (second submission for same pair updates, not duplicates)
    - Test zero-count response for an unknown `item_id`
    - Test `FeedbackStoreError` raised when the database is unavailable (mock the connection)
    - _Requirements: 12.4, 12.6, 12.11_

- [x] 13. Flask REST API
  - [x] 13.1 Implement `app/api.py`: Flask application factory and route registration
    - Create `create_app(config_manager)` factory; register blueprints for `/recommend` and `/feedback`
    - Wire `LanguageDetector`, `SemanticRetriever`, `KeywordRetriever`, `WebRetriever`, `HybridRanker`, `ContentVerifier`, `FeedbackStore` as application-scoped singletons initialized at startup
    - _Requirements: 11.1, 11.12_

  - [x] 13.2 Implement `POST /recommend` endpoint
    - Validate request body: `title` must be 3–500 characters after stripping whitespace and must contain at least one non-whitespace, non-punctuation character; return HTTP 422 with localized error on violation
    - Detect `query_language` via `LanguageDetector`
    - Run `SemanticRetriever`, `KeywordRetriever`, and `WebRetriever` in parallel using `concurrent.futures.ThreadPoolExecutor` with `component_timeout_seconds`
    - Handle retriever failures: fall back to available results, add localized notices; return HTTP 500 if both article retrievers fail
    - Fuse results via `HybridRanker`, verify via `ContentVerifier`, serialize to `RecommendResponse`
    - Return HTTP 200 with JSON; enforce `request_timeout_seconds` overall
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 5.4, 5.6, 5.9, 5.10, 5.11, 5.12, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 11.3, 11.4_

  - [x] 13.3 Implement `POST /feedback` endpoint
    - Validate `rating` is an integer in `[1, 5]`; validate `item_id` and `query` are non-empty; return HTTP 422 on violation
    - Call `FeedbackStore.upsert_rating`; return HTTP 503 with structured error if `FeedbackStoreError` is raised
    - Return localized success message based on `query_language` (detect from request or default to `"en"`)
    - _Requirements: 12.1, 12.2, 12.3, 12.11, 12.12, 12.13_

  - [x] 13.4 Implement `GET /feedback/{item_id}` endpoint
    - Accept optional `session_id` query parameter
    - Call `FeedbackStore.get_ratings`; return `FeedbackQueryResult` as JSON
    - Return HTTP 503 if `FeedbackStoreError` is raised
    - _Requirements: 12.5, 12.6_

  - [ ]* 13.5 Write unit tests for the API layer
    - Test HTTP 422 on invalid query (title too short, too long, whitespace-only)
    - Test HTTP 422 on invalid rating value (0, 6, float, string)
    - Test HTTP 503 when `FeedbackStore` is unavailable (mock the store)
    - Test correct JSON serialization: `quality_warning` is omitted (not `null`) when not set
    - _Requirements: 1.4, 1.5, 12.3, 12.11_

- [x] 14. Checkpoint — backend API complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Plain HTML/CSS/JS frontend
  - [x] 15.1 Create `static/index.html`
    - Input form with: thesis title text field (required), abstract textarea (optional), keywords input (optional), submit button, language toggle (RO / EN)
    - Two result sections with headings: "Articles" / "Articole" and "Web Resources" / "Resurse Web"
    - Loading spinner element (hidden by default)
    - Error message container (hidden by default)
    - _Requirements: 11.2, 11.5, 11.10_

  - [x] 15.2 Create `static/style.css`
    - Style result cards for articles and web resources
    - Style the quality warning badge in yellow/amber (`quality_warning` indicator)
    - Style the star rating control (1–5 stars, interactive)
    - Style the loading spinner and error message container
    - _Requirements: 11.6, 11.7, 11.13, 11.14_

  - [x] 15.3 Create `static/app.js`
    - Implement form submission: `POST /recommend` via `fetch`, display loading indicator, disable submit button during request
    - Render article cards: title, authors, year, abstract snippet, score badge, resource type badge, DOI/URL link where available, quality warning badge where `quality_warning` is set
    - Render web resource cards: title, clickable URL, snippet, web score badge, resource type badge, page keywords where available, quality warning badge where `quality_warning` is set
    - Display inline error message on API error without page reload
    - Implement language toggle: update all static labels, placeholders, and section headings immediately on toggle without page reload
    - _Requirements: 11.3, 11.5, 11.6, 11.7, 11.8, 11.9, 11.10, 11.11, 11.13, 11.14_

  - [x] 15.4 Implement star rating controls in `static/app.js`
    - Render a 1–5 star rating control on each result card
    - On star click: `POST /feedback` asynchronously with `item_id`, `query`, `rating`, `session_id`
    - On card render: `GET /feedback/{item_id}?session_id=...` to pre-populate the user's previous rating
    - Display average rating and total rating count on each card where available
    - Localize the rating label: `"Utilitate"` (ro) / `"Usefulness"` (en)
    - _Requirements: 11.15, 11.16, 11.17, 11.18, 11.19_

  - [x] 15.5 Register static file serving in Flask
    - Configure Flask to serve `static/` from the same origin as the REST API
    - Add a root route `GET /` that serves `index.html`
    - _Requirements: 11.1, 11.12_

- [x] 16. Feedback signal boost — wire into HybridRanker
  - [x] 16.1 Inject `FeedbackStore` into `HybridRanker.fuse_articles`
    - When `feedback_signal_enabled=True`, query `FeedbackStore.get_ratings` for each candidate article after RRF scoring; apply boost `boosted = rrf_score + feedback_signal_boost * (avg_rating - 1) / 4` for items with `avg_rating >= feedback_signal_min_rating`
    - When `feedback_signal_enabled=False`, skip all FeedbackStore queries
    - _Requirements: 12.8, 12.9, 12.10_

  - [ ]* 16.2 Write property test for feedback signal boost monotonicity
    - **Property 8: Feedback signal boost monotonicity**
    - Generate result sets with random average ratings; verify every item's boosted score `>= unboosted` when `feedback_signal_enabled=True`; verify every item's score equals its unboosted score when `feedback_signal_enabled=False`
    - **Validates: Requirements 12.8, 12.9**

- [ ] 17. Multilingual message localization
  - [x] 17.1 Implement `app/i18n.py`: localization helper
    - Define the full message table from the design (all keys: `no_articles`, `no_web_resources`, `semantic_unavailable`, `keyword_unavailable`, `web_unavailable`, `quality_warning`, `rating_saved`, `rating_invalid`)
    - Implement `t(key, language)` returning the correct string for `"ro"` or `"en"`
    - _Requirements: 5.9, 9.1, 9.2, 9.3, 9.4, 10.8, 10.9, 10.10, 12.12, 12.13_

  - [x] 17.2 Replace all inline message strings in API routes, `HybridRanker`, and `ContentVerifier` with calls to `t(key, query_language)`
    - _Requirements: 5.9, 10.8, 10.9, 10.10_

- [-] 18. Integration wiring and end-to-end validation
  - [x] 18.1 Create `app/main.py` entry point
    - Instantiate `ConfigManager`, build all components, call `create_app`, run Flask dev server
    - Add a CLI command `ingest` that accepts `--file` and `--format` arguments and calls `IngestionPipeline.ingest_file`
    - _Requirements: 7.1, 11.1_

  - [x] 18.2 Write integration tests
    - End-to-end `POST /recommend` with a small in-memory article corpus: verify response structure, score ranges in `[0.0, 1.0]`, `resource_type` labels, and `quality_warning` presence/absence
    - `POST /feedback` → `GET /feedback/{item_id}` round-trip against a real SQLite `FeedbackStore`
    - `ContentVerifier` with real embedding model: verify blocklisted domain is excluded; verify flagged item carries correct localized warning
    - _Requirements: 5.1, 5.2, 5.4, 5.10, 12.2, 12.5, 5b.9, 5b.11, 5b.12_

- [x] 19. Final checkpoint — full system integration
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints at tasks 7, 11, 14, and 19 ensure incremental validation
- Property tests (Properties 1–8) validate universal correctness invariants using `hypothesis`
- Unit tests validate specific examples, edge cases, and error conditions
- The embedding model (`paraphrase-multilingual-mpnet-base-v2`) is loaded once at startup and shared across `SemanticRetriever` and `ContentVerifier`
- FAISS index and BM25 index must be rebuilt after ingestion; the ingestion CLI handles this
