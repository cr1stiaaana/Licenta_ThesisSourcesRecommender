# Arhitectura Backend — Hybrid Thesis Recommender

## 1. Prezentare Generală

Backend-ul este o aplicație **Flask** (Python 3.10+) care expune un REST API pentru recomandări de articole academice. Arhitectura urmează principiile:
- **Application Factory Pattern** — `create_app()` pentru testabilitate
- **Blueprint-based routing** — separare logică pe domenii (recommend, feedback, auth)
- **Dependency Injection** — componentele sunt instanțiate la startup și injectate în blueprints
- **Graceful Degradation** — dacă un retriever eșuează, sistemul continuă cu ce e disponibil

## 2. Entry Point (`app/main.py`)

Aplicația are două moduri de operare:

```bash
# Server web (implicit)
python app/main.py serve --host 0.0.0.0 --port 5000 --debug

# Ingestie articole
python app/main.py ingest --file data/articles.json --format json
```

La pornire:
1. `ConfigManager` încarcă `config.yaml` și pornește watchdog-ul pentru hot-reload
2. `create_app()` instanțiază toate componentele (retrievers, ranker, verifier, stores)
3. Flask servește atât API-ul REST cât și frontend-ul static

## 3. Componente Principale

### 3.1 Fluxul unei Cereri de Recomandare

```
POST /recommend {"title": "...", "abstract": "...", "keywords": [...]}
         │
         ▼
┌─────────────────────┐
│  Validare Input     │  title: 3-500 chars, non-whitespace
│  (422 dacă invalid) │
└─────────┬───────────┘
         │
         ▼
┌─────────────────────┐
│  Language Detector  │  langdetect + langid ensemble → "ro" | "en"
└─────────┬───────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│         ThreadPoolExecutor (max_workers=4)       │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────┐│
│  │  Semantic    │  │  Keyword     │  │  Web   ││
│  │  Retriever   │  │  Retriever   │  │Retriever│
│  │  (FAISS)    │  │  (BM25)      │  │(DDG)   ││
│  └──────┬───────┘  └──────┬───────┘  └───┬────┘│
│         │                  │              │     │
│  ┌──────────────┐                              │
│  │  Academic    │                              │
│  │  Web Retriever│                              │
│  │(Semantic Scholar + arXiv)                    │
│  └──────────────┘                              │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Hybrid Ranker      │  RRF fusion + deduplication + feedback boost
└─────────┬───────────┘
         │
         ▼
┌─────────────────────┐
│  Content Verifier   │  Clickbait detection + domain blocklist
└─────────┬───────────┘
         │
         ▼
    JSON Response (200)
```

### 3.2 Execuție Paralelă

Retriever-ii rulează **în paralel** folosind `concurrent.futures.ThreadPoolExecutor`:

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        "semantic": executor.submit(semantic_retriever.retrieve, query, top_k),
        "keyword": executor.submit(keyword_retriever.retrieve, query, top_k),
        "academic_web": executor.submit(academic_web_retriever.retrieve, query, top_k),
        "web": executor.submit(web_retriever.retrieve, query, language),
    }
```

Fiecare retriever are un timeout configurat (`component_timeout_seconds`, default 3s). Dacă un retriever depășește timeout-ul, se adaugă un notice în răspuns și se continuă cu rezultatele disponibile.

## 4. Componente Detaliate

### 4.1 ArticleStore (`app/article_store.py`)

Stratul de stocare unificat care combină:
- **FAISS IndexFlatIP** — index vectorial pentru embeddings (768 dimensiuni)
- **SQLite** — metadata articole (titlu, autori, abstract, DOI, URL, keywords, limbă)

```python
class ArticleStore:
    def add_article(article, embedding)     # Upsert articol + vector
    def search_vector(query_embedding, k)   # Căutare cosine similarity
    def get_all_texts()                     # Corpus tokenizat pentru BM25
    def get_all_articles_ordered()          # Articole în ordinea FAISS index
    def get_article_by_id(id)               # Lookup metadata
```

**Deduplicare**: Articolele sunt identificate prin SHA-256 al DOI-ului (sau titlul normalizat dacă DOI lipsește).

**Persistență**: Indexul FAISS se salvează pe disc la fiecare `add_article()`. SQLite oferă ACID compliance.

### 4.2 SemanticRetriever (`app/retrievers/semantic.py`)

Căutare semantică bazată pe embeddings:

- **Model**: `paraphrase-multilingual-mpnet-base-v2` (sentence-transformers)
- **Dimensiune vector**: 768
- **Similaritate**: Cosine similarity (inner product pe vectori normalizați)
- **Cross-lingual**: Query în română găsește articole în engleză și invers

```python
class SemanticRetriever:
    def encode(text: str) -> np.ndarray       # Generare embedding (768-dim)
    def retrieve(query, top_k) -> RetrievalResult  # Căutare FAISS
```

**Normalizare**: Vectorii sunt normalizați L2 înainte de indexare, astfel inner product = cosine similarity.

**Partajare model**: Același model este folosit și de `ContentVerifier` (o singură instanță în memorie, ~420MB).

### 4.3 KeywordRetriever (`app/retrievers/keyword.py`)

Căutare lexicală bazată pe BM25:

- **Algoritm**: Okapi BM25 (k1=1.5, b=0.75)
- **Tokenizare**: Lowercase + split pe whitespace/punctuație
- **Index**: Serializat cu pickle la `data/bm25.pkl`
- **Normalizare scoruri**: Împărțire la scorul maxim → [0.0, 1.0]

```python
class KeywordRetriever:
    def retrieve(query, top_k) -> RetrievalResult
```

**Complementaritate cu semantic**: BM25 prinde termeni tehnici exacți (ex: "FAISS", "BM25") pe care embeddings-urile le pot dilua în spațiul vectorial.

### 4.4 WebRetriever (`app/retrievers/web.py`)

Căutare web live la query time:

- **Provider implicit**: DuckDuckGo (fără API key)
- **Provideri alternativi**: Google CSE, Bing (cu API key)
- **Scor**: Bazat pe rank: `web_score = 1.0 / (rank + 1)`, normalizat
- **Bilingual**: Opțional, queries paralele în RO + EN, deduplicate pe URL

### 4.5 AcademicWebRetriever (`app/retrievers/academic_web.py`)

Căutare în baze de date academice:
- **Semantic Scholar API** — articole peer-reviewed cu metadata completă
- **arXiv API** — preprint-uri din Computer Science, Mathematics, Physics

Rezultatele sunt tratate ca articole suplimentare și fuzionate cu cele din corpus.

### 4.6 HybridRanker (`app/rankers/hybrid.py`)

Fuzionează rezultatele din toți retriever-ii:

**Reciprocal Rank Fusion (RRF)** — strategia implicită:
```
RRF_score(d) = Σ_r  weight_r / (60 + rank_r(d))
```

- `weight_semantic = 0.6`, `weight_keyword = 0.4` (configurabile)
- `k = 60` (constantă standard din paper-ul original RRF)
- Deduplicare pe DOI sau titlu normalizat

**Feedback Signal Boost** (opțional):
```
boosted_score = rrf_score + 0.1 × (avg_rating - 1) / 4
```
Articolele cu rating mediu ≥ 4.0 primesc un boost mic.

**Alternativă**: Weighted sum (selectabilă din `config.yaml`):
```
score = semantic_weight × sem_score + keyword_weight × kw_score
```

### 4.7 ContentVerifier (`app/verifiers/content.py`)

Detectare clickbait și filtrare calitate:

1. Calculează `title_sim = cosine(query_embedding, embed(title))`
2. Calculează `content_sim = cosine(query_embedding, embed(abstract/snippet))`
3. Dacă `title_sim - content_sim > mismatch_threshold (0.3)`:
   - `Quality_Score = score × (1 - (title_sim - content_sim))`
   - Setează `quality_warning` localizat
4. Dacă `Quality_Score < min_score` → exclude articolul
5. Verifică URL-uri contra `domain_blocklist` → exclude dacă match

**Nu face HTTP requests** — folosește doar datele deja disponibile (abstract, snippet).

### 4.8 FeedbackStore (`app/feedback/store.py`)

Persistență rating-uri utilizatori:

- **SQLite** la `data/feedback.db`
- **Schema**: `ratings(item_id, session_id, query, rating, updated_at)` cu UNIQUE pe `(item_id, session_id)`
- **Upsert**: `INSERT OR REPLACE` — al doilea rating pentru același item actualizează, nu duplică

```python
class FeedbackStore:
    def upsert_rating(item_id, query, rating, session_id, timestamp)
    def get_ratings(item_id, session_id) -> FeedbackQueryResult
```

### 4.9 UserStore (`app/auth/user_store.py`)

Autentificare și articole salvate:
- Înregistrare/login cu bcrypt password hashing
- Session-based auth (Flask sessions)
- Salvare/ștergere articole favorite per utilizator

### 4.10 LanguageDetector (`app/language_detector.py`)

Detectare limbă cu ensemble voting:
- `langdetect` + `langid` — dacă ambele sunt de acord, se folosește rezultatul
- Dacă nu sunt de acord sau aruncă excepție → default `"en"`
- Robust pentru texte scurte (titluri de 5-15 cuvinte)

### 4.11 ConfigManager (`app/config_manager.py`)

Configurare hot-reloadable:
- Citește `config.yaml` la startup
- `watchdog` monitorizează fișierul pentru modificări
- La schimbare: re-validează, aplică dacă valid, păstrează config vechi dacă invalid
- Niciun restart necesar

### 4.12 i18n (`app/i18n.py`)

Internaționalizare bilingvă:
- Funcție `t(key, language)` → string localizat
- Suport RO + EN pentru toate mesajele user-facing
- Chei: `no_articles`, `no_web_resources`, `semantic_unavailable`, `keyword_unavailable`, `web_unavailable`, `quality_warning`, `rating_saved`, `rating_invalid`

## 5. REST API Endpoints

### 5.1 `POST /recommend`

| Câmp | Tip | Obligatoriu | Descriere |
|------|-----|:-----------:|-----------|
| `title` | string | ✅ | Titlu teză (3-500 chars) |
| `abstract` | string | ❌ | Abstract opțional |
| `keywords` | string[] | ❌ | Cuvinte cheie |
| `offset` | int | ❌ | Offset paginare (default 0) |
| `type` | string | ❌ | `"articles"`, `"web"`, `"both"` (default) |

**Răspuns (200)**:
```json
{
  "query_language": "en",
  "articles": [
    {
      "resource_type": "article",
      "title": "...",
      "authors": ["..."],
      "year": 2023,
      "abstract_snippet": "...",
      "score": 0.87,
      "doi": "...",
      "url": "...",
      "item_id": "sha256..."
    }
  ],
  "web_resources": [
    {
      "resource_type": "web",
      "title": "...",
      "url": "...",
      "snippet": "...",
      "web_score": 0.72,
      "keywords": ["..."],
      "item_id": "sha256..."
    }
  ],
  "notices": []
}
```

**Erori**: 422 (validare), 500 (toți retriever-ii eșuează)

### 5.2 `POST /feedback`

```json
{"item_id": "...", "query": "...", "rating": 4, "session_id": "..."}
```
→ `{"message": "Rating saved."}` (200) sau 422/503

### 5.3 `GET /feedback/<item_id>?session_id=...`

→ `{"item_id": "...", "user_rating": 4, "average_rating": 3.7, "rating_count": 12}`

### 5.4 Auth Endpoints

| Endpoint | Metodă | Descriere |
|----------|--------|-----------|
| `/auth/register` | POST | Creare cont |
| `/auth/login` | POST | Autentificare |
| `/auth/logout` | POST | Deconectare |
| `/auth/me` | GET | User curent |
| `/saved` | GET/POST | Articole salvate |
| `/saved/<id>` | DELETE | Ștergere salvare |
| `/saved/<id>/check` | GET | Verificare dacă e salvat |

## 6. Data Models (`app/models.py`)

Toate modelele sunt **dataclasses** Python:

```python
@dataclass
class Query:
    title: str
    abstract: str | None = None
    keywords: list[str] = field(default_factory=list)
    
    def combined_text(self) -> str:
        """Concatenează title + abstract + keywords pentru embedding."""

@dataclass
class Article:
    id: str                    # SHA-256 hash
    title: str
    abstract: str | None
    authors: list[str]
    year: int | None
    doi: str | None
    url: str | None
    keywords: list[str]
    language: str              # "ro" | "en"

@dataclass
class ScoredArticle:
    article: Article
    score: float               # [0.0, 1.0]

@dataclass
class RetrievalResult:
    items: list[ScoredArticle]
    source: str                # "semantic" | "keyword"

@dataclass
class ArticleRecommendation:
    resource_type: str = "article"
    title: str
    authors: list[str]
    year: int | None
    abstract_snippet: str      # max 300 chars
    score: float
    doi: str | None
    url: str | None
    quality_warning: str | None
    item_id: str

@dataclass
class WebResourceRecommendation:
    resource_type: str = "web"
    title: str
    url: str
    snippet: str
    web_score: float
    keywords: list[str]
    quality_warning: str | None
    item_id: str
```

## 7. Configurare (`app/config.py`)

`AppConfig` dataclass cu toate parametrii tunabili:

| Parametru | Default | Descriere |
|-----------|---------|-----------|
| `semantic_weight` | 0.6 | Pondere semantic în RRF |
| `keyword_weight` | 0.4 | Pondere keyword în RRF |
| `article_top_k` | 10 | Max articole returnate |
| `web_top_k` | 10 | Max resurse web returnate |
| `min_article_score` | 0.1 | Prag minim scor articole |
| `min_web_score` | 0.1 | Prag minim scor web |
| `mismatch_threshold` | 0.3 | Prag clickbait detection |
| `component_timeout_seconds` | 3.0 | Timeout per retriever |
| `request_timeout_seconds` | 5.0 | Timeout total request |
| `fusion_strategy` | "rrf" | "rrf" sau "weighted_sum" |
| `feedback_signal_enabled` | false | Activare feedback boost |
| `web_search_provider` | "duckduckgo" | Provider web search |
| `embedding_model` | "paraphrase-multilingual-mpnet-base-v2" | Model embeddings |

## 8. Baze de Date

### 8.1 `data/articles.db` (SQLite)
```sql
CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    authors TEXT,          -- JSON array
    year INTEGER,
    doi TEXT,
    url TEXT,
    keywords TEXT,         -- JSON array
    language TEXT,
    faiss_idx INTEGER      -- Poziție în indexul FAISS
);
```

### 8.2 `data/feedback.db` (SQLite)
```sql
CREATE TABLE ratings (
    item_id TEXT,
    session_id TEXT,
    query TEXT,
    rating INTEGER,        -- [1, 5]
    updated_at TIMESTAMP,
    UNIQUE(item_id, session_id)
);
```

### 8.3 `data/users.db` (SQLite)
Conturi utilizatori + articole salvate.

### 8.4 `data/faiss.index` (Binary)
Index vectorial FAISS cu embeddings 768-dimensionale.

### 8.5 `data/bm25.pkl` (Pickle)
Index BM25 serializat (rank_bm25.BM25Okapi).

## 9. Error Handling și Resilience

| Scenariul | Comportament |
|-----------|-------------|
| SemanticRetriever eșuează | Fallback la keyword-only + notice |
| KeywordRetriever eșuează | Fallback la semantic-only + notice |
| Ambii retriever-i eșuează | HTTP 500 cu mesaj localizat |
| WebRetriever eșuează | Continuă cu articole only + notice |
| FeedbackStore indisponibil | HTTP 503 pe endpoint-urile de feedback |
| ContentVerifier eșuează | Skip verificare, returnează rezultate neverificate |
| Timeout pe un retriever | Skip retriever, adaugă notice |
| Config invalid | Păstrează config anterior, log warning |

## 10. Performanță

| Operație | Timp tipic |
|----------|-----------|
| Encoding query (sentence-transformers) | ~50ms |
| FAISS search (1000 articole) | ~1ms |
| BM25 search (1000 articole) | ~5ms |
| Web search (DuckDuckGo) | ~500-2000ms |
| Academic search (Semantic Scholar) | ~300-1000ms |
| Total request (paralel) | ~1-3s |

**Optimizări implementate**:
- Retriever-i în paralel (ThreadPoolExecutor)
- Model încărcat o singură dată la startup
- FAISS inner product pe vectori normalizați (evită calcul cosine explicit)
- BM25 index pre-calculat și serializat
- Timeout per componentă (nu blochează indefinit)
