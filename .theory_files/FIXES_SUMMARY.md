# Article Retrieval and Keyword Search Fixes

## Summary

✅ **All issues resolved!** The system now returns both articles and web resources correctly.

## Issues Identified and Fixed

### 1. Article Retrieval Not Working
**Root Cause**: FAISS index and database were out of sync
- FAISS index had 15 vectors (indices 0-14)
- Articles in database had faiss_idx values 10-14
- This mismatch caused ArticleStore lookups to fail

**Fix**: Rebuilt indexes with proper alignment (faiss_idx 0-9 for 10 articles)

### 2. Keyword Retrieval Unavailable
**Root Cause**: BM25 tokenization mismatch
- `KeywordRetriever._tokenize()` lowercased tokens
- `ArticleStore.get_all_texts()` did NOT lowercase tokens
- Query tokens like "spec" couldn't match corpus tokens like "Specification"

**Fix**: Updated `ArticleStore.get_all_texts()` to lowercase and tokenize consistently

### 3. Semantic Scores > 1.0
**Root Cause**: Embeddings were not normalized
- FAISS IndexFlatIP expects unit-normalized vectors for cosine similarity
- Embeddings were added without normalization
- Query vectors were also not normalized

**Fix**: Normalize all embeddings to unit length before adding to FAISS

### 4. HybridRanker Filtering Out All Articles
**Root Cause**: `min_article_score` threshold too high for RRF scores
- RRF produces scores in range [0.0, 0.02]
- Config had `min_article_score: 0.1` which filtered out all results

**Fix**: Changed `min_article_score: 0.001` to allow RRF scores through

### 5. Test Articles Had Poor Abstracts
**Root Cause**: Original test articles had minimal abstracts
- Made semantic search less effective
- Didn't represent real academic content

**Fix**: Added 10 realistic articles from arXiv with proper abstracts:
- Formal specification papers (arXiv 2404.18515, 2401.08807)
- Property-based testing papers (arXiv 2510.09907, 2602.18545)
- Test-driven development papers (arXiv 2011.11942)
- Classic papers (Beck's TDD, QuickCheck, BDD with Cucumber, etc.)

## Files Modified

1. **app/article_store.py** - Fixed tokenization in `get_all_texts()`
2. **app/retrievers/semantic.py** - Added normalization to `encode()`, fixed score handling
3. **config.yaml** - Changed `min_article_score` from 0.1 to 0.001
4. **populate_article_store.py** - Added embedding normalization
5. **rebuild_indexes.py** - Complete rebuild script with all fixes
6. **add_realistic_articles.py** - Script to add 10 realistic articles from arXiv

## Current Status

✅ **FAISS Index**: 10 vectors, properly normalized, aligned with database
✅ **BM25 Index**: 10 documents, properly tokenized (lowercased)
✅ **Database**: 10 articles with faiss_idx 0-9
✅ **SemanticRetriever**: Working, scores in [0, 1] range
✅ **KeywordRetriever**: Working, scores in [0, 1] range
✅ **HybridRanker**: Working, RRF scores in [0.001, 0.02] range
✅ **WebRetriever**: Working, returns 5 web resources

## Test Results

Query: "spec driven dev"

**Articles** (5 results):
1. Test-Driven Development: By Example (0.016)
2. A Family of Experiments on Test-Driven Development (0.016)
3. The Cucumber Book: Behaviour-Driven Development for Testers (0.016)
4. QuickCheck: A Lightweight Tool for Random Testing of Haskell (0.015)
5. Formal Methods: State of the Art and New Directions (0.010)

**Web Resources** (5 results):
1. Spec-driven development (1.000)
2. Spec-driven development (0.500)
3. Understanding Spec-Driven-Development (0.333)
4. Spec-Driven Development: 10 things you need to know (0.250)
5. Spec Driven Development with Rovo Dev (0.200)

## Next Steps

⚠️ **IMPORTANT**: You MUST restart the Flask server for changes to take effect!

The server loads ArticleStore, SemanticRetriever, and KeywordRetriever at startup. The updated indexes and code changes will only be used after a restart.

### To Restart:
1. Stop the current Flask server (Ctrl+C)
2. Start it again: `python app/main.py` (or however you normally start it)
3. Test with query "spec driven dev" in the UI

### Expected Behavior After Restart:
- **Articles tab**: Shows 5 academic articles with proper titles, authors, years, and abstracts
- **Web Resources tab**: Shows 5 web results from DuckDuckGo
- Both tabs have proper scores
- "Load More" button works for pagination (fetches next 5 results with offset)
- All articles have realistic content from arXiv and academic sources

## Article Database

The system now contains 10 high-quality academic articles:

1. **An Agile Formal Specification Language Design Based on K Framework** (2024)
   - arXiv:2404.18515
   - Formal methods, specification languages, agile development

2. **Automated Generation of Formal Program Specifications via Large Language Models** (2024)
   - arXiv:2401.08807
   - LLM-based specification generation, SpecGen tool

3. **Agentic Property-Based Testing: Finding Bugs Across the Python Ecosystem** (2025)
   - arXiv:2510.09907
   - LLM agents for property-based testing, found bugs in NumPy

4. **Programmable Property-Based Testing** (2026)
   - arXiv:2602.18545
   - Advanced PBT framework design, deferred binding abstract syntax

5. **A Family of Experiments on Test-Driven Development** (2020)
   - arXiv:2011.11942
   - Meta-analysis of 12 TDD experiments in academia and industry

6. **Test-Driven Development: By Example** (2003)
   - Kent Beck's classic book on TDD

7. **The Cucumber Book: Behaviour-Driven Development for Testers and Developers** (2017)
   - BDD with Cucumber, executable specifications

8. **Formal Methods: State of the Art and New Directions** (1996)
   - Clarke & Wing's survey of formal methods

9. **QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs** (2000)
   - Original QuickCheck paper by Claessen & Hughes

10. **From Specification to Implementation: A Refinement-Based Approach** (1998)
    - Refinement calculus, correctness preservation

## Maintenance Notes

### Adding New Articles
When adding new articles, always:
1. Normalize embeddings: `embedding = embedding / np.linalg.norm(embedding)`
2. Use `ArticleStore.add_article()` to ensure proper faiss_idx
3. Rebuild BM25 index after adding articles (or delete `data/bm25.pkl` to force rebuild)

### Rebuilding Indexes
If indexes get corrupted or out of sync:
```bash
python rebuild_indexes.py
```

### Adding More Realistic Articles
To add more articles from arXiv:
```bash
python add_realistic_articles.py
```

Then rebuild BM25:
```bash
python -c "from app.article_store import ArticleStore; from app.config_manager import ConfigManager; from rank_bm25 import BM25Okapi; import pickle; config = ConfigManager('config.yaml').get(); store = ArticleStore(config.vector_store_path, config.metadata_db_path); corpus = store.get_all_texts(); bm25 = BM25Okapi(corpus); pickle.dump(bm25, open('data/bm25.pkl', 'wb'))"
```

### Configuration Notes

**Important**: The `min_article_score` threshold depends on the fusion strategy:
- **RRF** (default): Use `min_article_score: 0.001` (RRF scores are typically 0.001-0.02)
- **weighted_sum**: Use `min_article_score: 0.1` (weighted scores are typically 0.1-1.0)

If you change `fusion_strategy` in config.yaml, adjust `min_article_score` accordingly.
