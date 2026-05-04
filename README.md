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
- **Frontend**: TypeScript, HTML, CSS (compiled to JavaScript)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cr1stiaaana/Licenta_ThesisSourcesRecommender.git
cd Licenta_ThesisSourcesRecommender
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies and build frontend:
```bash
npm install
npm run build
```

4. Add articles to the database:
```bash
python add_realistic_articles.py
```

5. Start the server:
```bash
python app/main.py
```

6. Open http://localhost:5000 in your browser

## Development

### Frontend Development

The frontend is written in TypeScript and compiled to JavaScript.

**Build once:**
```bash
npm run build
```

**Watch mode (auto-rebuild on changes):**
```bash
npm run watch
```

**TypeScript source files:**
- `static/src/api.ts` - API client functions
- `static/src/app.ts` - Main application logic
- `static/src/types.ts` - Type definitions

**Compiled output:**
- `static/dist/` - Compiled JavaScript files (auto-generated, do not edit)

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
├── static/
│   ├── src/                # TypeScript source files
│   │   ├── api.ts          # API client
│   │   ├── app.ts          # Main application
│   │   └── types.ts        # Type definitions
│   ├── dist/               # Compiled JavaScript (auto-generated)
│   ├── index.html          # Main HTML
│   └── style.css           # Styles
├── tests/                  # Integration tests
├── config.yaml             # Configuration
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript configuration
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
