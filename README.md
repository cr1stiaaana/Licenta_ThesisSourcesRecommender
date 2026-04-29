# Thesis Sources Recommender

A hybrid recommendation system for academic thesis research that combines semantic search, keyword matching, and web retrieval to suggest relevant articles and resources.

## Features

- **Hybrid Article Retrieval**: Combines semantic (FAISS) and keyword (BM25) search
- **Web Search Integration**: DuckDuckGo web search for additional resources
- **Academic API Integration**: Semantic Scholar and arXiv for live academic articles
- **Two-Column UI**: Clean interface with tabs for Articles and Web Resources
- **Pagination**: Load more results with offset-based pagination
- **Dark Mode**: Toggle between light and dark themes
- **Bilingual Support**: Romanian and English interface

## Tech Stack

- **Backend**: Flask, Python 3.10+
- **Search**: FAISS (semantic), BM25 (keyword)
- **Embeddings**: sentence-transformers (paraphrase-multilingual-mpnet-base-v2)
- **Database**: SQLite
- **Frontend**: Vanilla JavaScript, HTML, CSS

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cr1stiaaana/Licenta_ThesisSourcesRecommender.git
cd Licenta_ThesisSourcesRecommender
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add articles to the database:
```bash
python add_realistic_articles.py
```

4. Start the server:
```bash
python app/main.py
```

5. Open http://localhost:5000 in your browser

## Usage

1. Enter your thesis title in the search box
2. Optionally add abstract and keywords
3. Click "Caută Surse" (Search Sources)
4. Browse results in the Articles and Web Resources tabs
5. Click "Load More" for additional results

## Configuration

Edit `config.yaml` to customize:
- Retrieval weights (semantic vs keyword)
- Top-K limits
- Minimum score thresholds
- Web search provider
- Timeouts

## Project Structure

```
├── app/
│   ├── api.py              # Flask REST API
│   ├── article_store.py    # FAISS + SQLite storage
│   ├── retrievers/         # Semantic, keyword, web retrievers
│   ├── rankers/            # Hybrid ranking (RRF)
│   ├── verifiers/          # Content quality verification
│   └── web_search/         # Web search adapters
├── static/                 # Frontend (HTML, CSS, JS)
├── tests/                  # Integration tests
├── config.yaml             # Configuration
└── requirements.txt        # Python dependencies
```

## Database

The system includes 10 realistic academic articles from arXiv:
- Formal specification papers
- Property-based testing papers
- Test-driven development papers
- Classic papers (Beck's TDD, QuickCheck, BDD)

## License

MIT License

## Author

Cristiana - ETTI, Politehnica București
