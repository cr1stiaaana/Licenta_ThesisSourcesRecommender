# Product Overview

## Hybrid Thesis Recommender

An academic research recommendation system that helps students and researchers discover relevant articles and resources for their thesis work.

## Core Functionality

- **Hybrid Retrieval**: Combines semantic search (FAISS embeddings) with keyword matching (BM25) to find relevant academic articles
- **Web Search Integration**: Supplements local corpus with live web results from DuckDuckGo, Google CSE, or Bing
- **Academic APIs**: Integrates with Semantic Scholar and arXiv for real-time academic content
- **Quality Verification**: Content verifier detects clickbait and low-quality results using embedding similarity
- **User Feedback**: Rating system (1-5 stars) with optional feedback signal boosting
- **Bilingual Support**: Romanian and English interface with language detection
- **User Authentication**: Registration, login, and saved items functionality

## Key Features

- Two-column UI with separate tabs for Articles and Web Resources
- Pagination with offset-based "Load More"
- Dark mode toggle
- Hot-reloadable YAML configuration
- Domain blocklist for filtering unwanted sources
- Localized quality warnings for suspicious content
