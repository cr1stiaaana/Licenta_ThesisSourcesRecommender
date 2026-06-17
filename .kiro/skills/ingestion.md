---
name: ingestion
description: Ghid pentru adăugarea de articole noi în sistem (JSON, CSV, BibTeX).
version: 1.0.0
---

# Skill: Article Ingestion

## Overview

This skill guides the process of adding new articles to the system — from sourcing to indexing.

## Supported Formats

| Format | Extension | Parser |
|--------|-----------|--------|
| JSON | `.json` | Built-in `json` module |
| CSV | `.csv` | `csv` module |
| BibTeX | `.bib` | `bibtexparser` |

## Required Fields

| Field | Required | Description |
|-------|:--------:|-------------|
| `title` | ✅ | Article title (3-500 chars) |
| `abstract` | ✅ | Article abstract |
| `authors` | ❌ | Comma-separated or list |
| `year` | ❌ | Publication year |
| `doi` | ❌ | Digital Object Identifier |
| `url` | ❌ | Link to full text |
| `keywords` | ❌ | Comma-separated keywords |

## Commands

```bash
# Ingest from JSON
python app/main.py ingest --file data/articles.json --format json

# Ingest from CSV
python app/main.py ingest --file data/articles.csv --format csv

# Ingest from BibTeX
python app/main.py ingest --file data/refs.bib --format bibtex

# Rebuild indexes after ingestion
python rebuild_indexes.py
```

## JSON Format Example

```json
[
  {
    "title": "Hybrid Recommender Systems: Survey and Experiments",
    "abstract": "This paper surveys hybrid recommender systems...",
    "authors": "Robin Burke",
    "year": 2002,
    "doi": "10.1023/A:1021240730564",
    "url": "https://link.springer.com/article/10.1023/A:1021240730564",
    "keywords": "recommender systems, hybrid, collaborative filtering"
  }
]
```

## CSV Format Example

```csv
title,abstract,authors,year,doi,url,keywords
"Hybrid Recommender Systems","This paper surveys...","Robin Burke",2002,"10.1023/A:1021240730564","https://...","recommender systems, hybrid"
```

## Pipeline Steps

1. **Parse** file → extract article records
2. **Validate** each record (title + abstract required)
3. **Detect language** (ro/en) for each article
4. **Generate embedding** using `paraphrase-multilingual-mpnet-base-v2`
5. **Compute ID** as SHA-256 of DOI (or normalized title)
6. **Upsert** into SQLite metadata + FAISS vector index
7. **Update BM25** index with new corpus

## Post-Ingestion Checklist

- [ ] Run `python rebuild_indexes.py` to rebuild BM25
- [ ] Verify article count: `SELECT COUNT(*) FROM articles`
- [ ] Test a query to confirm new articles appear in results
- [ ] Check logs for skipped records (missing title/abstract)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Article skipped: missing title" | Ensure title field is non-empty |
| "Embedding model not loaded" | Run once to download model (~420MB) |
| FAISS index size mismatch | Delete `data/faiss.index` and rebuild |
| Duplicate articles | System uses upsert — same DOI/title won't duplicate |
