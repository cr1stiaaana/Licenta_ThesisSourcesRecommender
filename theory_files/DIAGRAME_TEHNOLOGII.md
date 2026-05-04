# Diagrame și Vizualizări - Tehnologii și Arhitectură

## 1. Stack Tehnologic - Vedere de Ansamblu

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   HTML5      │  │    CSS3      │  │ JavaScript   │      │
│  │              │  │              │  │   (ES6+)     │      │
│  │  Semantic    │  │  Variables   │  │   Vanilla    │      │
│  │  Structure   │  │  Dark Mode   │  │   Fetch API  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (Flask 3.1.1)                 │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐      │   │
│  │  │ Recommend  │ │  Feedback  │ │    Auth    │      │   │
│  │  │ Blueprint  │ │ Blueprint  │ │ Blueprint  │      │   │
│  │  └────────────┘ └────────────┘ └────────────┘      │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Business Logic Layer                       │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐      │   │
│  │  │  Hybrid    │ │  Content   │ │  Language  │      │   │
│  │  │  Ranker    │ │  Verifier  │ │  Detector  │      │   │
│  │  └────────────┘ └────────────┘ └────────────┘      │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Retrieval Layer                           │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐      │   │
│  │  │  Semantic  │ │  Keyword   │ │    Web     │      │   │
│  │  │ Retriever  │ │ Retriever  │ │ Retriever  │      │   │
│  │  │  (FAISS)   │ │   (BM25)   │ │  (DDG)     │      │   │
│  │  └────────────┘ └────────────┘ └────────────┘      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite     │  │    FAISS     │  │    BM25      │      │
│  │              │  │              │  │              │      │
│  │  articles.db │  │ faiss.index  │  │  bm25.pkl    │      │
│  │  feedback.db │  │              │  │              │      │
│  │   users.db   │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 2. Flux de Date - Request/Response

```
┌─────────┐
│ Client  │
│ Browser │
└────┬────┘
     │
     │ 1. POST /recommend
     │    { title: "machine learning" }
     ▼
┌─────────────────────────────────────────┐
│         Flask API Layer                 │
│  ┌───────────────────────────────────┐  │
│  │  1. Validate Input                │  │
│  │  2. Detect Language               │  │
│  │  3. Create Query Object           │  │
│  └───────────────────────────────────┘  │
└────┬────────────────────────────────────┘
     │
     │ 2. Parallel Retrieval
     ├──────────┬──────────┬──────────┐
     ▼          ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Semantic │ │Keyword  │ │Academic │ │   Web   │
│Retriever│ │Retriever│ │   API   │ │Retriever│
│         │ │         │ │         │ │         │
│  FAISS  │ │  BM25   │ │Semantic │ │DuckDuck │
│         │ │         │ │Scholar  │ │   Go    │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │          │          │          │
     │ 3. Results (top-20 each)       │
     └──────────┴──────────┴──────────┘
                  │
                  ▼
     ┌────────────────────────────┐
     │    Hybrid Ranker (RRF)     │
     │  - Fuse semantic + keyword │
     │  - Rank web resources      │
     │  - Apply score thresholds  │
     └────────────┬───────────────┘
                  │
                  │ 4. Ranked Results
                  ▼
     ┌────────────────────────────┐
     │    Content Verifier        │
     │  - Check quality           │
     │  - Detect clickbait        │
     │  - Add warnings            │
     └────────────┬───────────────┘
                  │
                  │ 5. Verified Results
                  ▼
     ┌────────────────────────────┐
     │    Response Builder        │
     │  - Apply pagination        │
     │  - Format JSON             │
     │  - Add metadata            │
     └────────────┬───────────────┘
                  │
                  │ 6. JSON Response
                  ▼
            ┌─────────┐
            │ Client  │
            │ Browser │
            └─────────┘
```

## 3. Arhitectura Modulară

```
app/
├── api.py                    # Flask application factory
│   ├── create_app()         # Main entry point
│   ├── _make_recommend_blueprint()
│   ├── _make_feedback_blueprint()
│   └── _make_auth_blueprint()
│
├── retrievers/              # Retrieval components
│   ├── semantic.py          # FAISS-based semantic search
│   ├── keyword.py           # BM25 keyword matching
│   ├── web.py               # Web search orchestrator
│   └── academic_web.py      # Semantic Scholar + arXiv
│
├── rankers/                 # Ranking algorithms
│   └── hybrid.py            # RRF + weighted sum fusion
│
├── verifiers/               # Quality control
│   └── content.py           # Clickbait detection
│
├── auth/                    # Authentication
│   └── user_store.py        # User management
│
├── feedback/                # User feedback
│   └── store.py             # Rating persistence
│
├── models.py                # Data models (dataclasses)
├── config.py                # Configuration schema
├── config_manager.py        # Hot-reload config
├── language_detector.py     # Language detection
└── i18n.py                  # Internationalization
```

## 4. Pipeline de Procesare Query

```
┌──────────────────────────────────────────────────────────────┐
│                    Query Processing Pipeline                  │
└──────────────────────────────────────────────────────────────┘

Input: "Neural networks for NLP"
  │
  ▼
┌─────────────────────────┐
│  1. Input Validation    │
│  - Length: 3-500 chars  │
│  - Non-empty content    │
│  - Sanitization         │
└───────────┬─────────────┘
            │ ✓ Valid
            ▼
┌─────────────────────────┐
│  2. Language Detection  │
│  - LangDetect           │
│  - LangID (fallback)    │
│  - Result: "en"         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  3. Query Embedding     │
│  - Model: mpnet-base-v2 │
│  - Dimension: 768       │
│  - Normalize L2         │
└───────────┬─────────────┘
            │
            ├─────────────────────────────────┐
            │                                 │
            ▼                                 ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│  4a. Semantic Search    │     │  4b. Keyword Search     │
│  - FAISS IndexFlatIP    │     │  - BM25 Tokenization    │
│  - Cosine similarity    │     │  - TF-IDF scoring       │
│  - Top-20 results       │     │  - Top-20 results       │
└───────────┬─────────────┘     └───────────┬─────────────┘
            │                               │
            └───────────┬───────────────────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │  5. Hybrid Fusion (RRF) │
            │  score = Σ weight/(k+r) │
            │  k = 60 (RRF constant)  │
            │  r = rank in list       │
            └───────────┬─────────────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │  6. Score Filtering     │
            │  - min_score: 0.001     │
            │  - Remove duplicates    │
            │  - Sort by score desc   │
            └───────────┬─────────────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │  7. Pagination          │
            │  - Offset: 0            │
            │  - Limit: 5             │
            │  - Type: articles/web   │
            └───────────┬─────────────┘
                        │
                        ▼
Output: Top-5 relevant articles
```

## 5. Spec-Driven Development Workflow

```
┌──────────────────────────────────────────────────────────────┐
│              Spec-Driven Development Cycle                    │
└──────────────────────────────────────────────────────────────┘

1. DEFINE SPEC
   ┌─────────────────┐
   │  openapi.yaml   │
   │  - Endpoints    │
   │  - Schemas      │
   │  - Validation   │
   └────────┬────────┘
            │
            ▼
2. GENERATE DOCS
   ┌─────────────────┐
   │ generate_docs.py│
   │  - Swagger UI   │
   │  - Redoc        │
   │  - Markdown     │
   └────────┬────────┘
            │
            ▼
3. IMPLEMENT
   ┌─────────────────┐
   │   app/api.py    │
   │  - Endpoints    │
   │  - Validation   │
   │  - Responses    │
   └────────┬────────┘
            │
            ▼
4. TEST CONTRACT
   ┌─────────────────┐
   │test_api_contract│
   │  - Schemas      │
   │  - Status codes │
   │  - Validation   │
   └────────┬────────┘
            │
            ▼
5. VALIDATE
   ┌─────────────────┐
   │  pytest -v      │
   │  - 23 tests     │
   │  - Coverage     │
   │  - Report       │
   └────────┬────────┘
            │
            ▼
6. ITERATE
   ┌─────────────────┐
   │  Adjust spec    │
   │  Fix issues     │
   │  Improve code   │
   └────────┬────────┘
            │
            └──────────┐
                       │
            ┌──────────▼────────┐
            │   PRODUCTION      │
            │   - Documented    │
            │   - Tested        │
            │   - Validated     │
            └───────────────────┘
```

## 6. Tehnologii ML/AI - Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│              Machine Learning Pipeline                        │
└──────────────────────────────────────────────────────────────┘

OFFLINE (Build Time):
┌─────────────────────────────────────────────────────────────┐
│  1. Data Ingestion                                          │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│     │  arXiv   │  │ Semantic │  │  Manual  │              │
│     │   API    │  │ Scholar  │  │  Import  │              │
│     └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│          └─────────────┴─────────────┘                      │
│                        │                                     │
│  2. Preprocessing                                           │
│     ┌────────────────────────────────┐                      │
│     │  - Clean text                  │                      │
│     │  - Extract metadata            │                      │
│     │  - Tokenize for BM25           │                      │
│     └────────────┬───────────────────┘                      │
│                  │                                           │
│  3. Embedding Generation                                    │
│     ┌────────────────────────────────┐                      │
│     │  SentenceTransformer           │                      │
│     │  Model: mpnet-base-v2          │                      │
│     │  Input: title + abstract       │                      │
│     │  Output: 768-dim vector        │                      │
│     └────────────┬───────────────────┘                      │
│                  │                                           │
│  4. Index Building                                          │
│     ┌──────────────┐  ┌──────────────┐                     │
│     │ FAISS Index  │  │  BM25 Index  │                     │
│     │ IndexFlatIP  │  │  Tokenized   │                     │
│     │ Normalized   │  │  Documents   │                     │
│     └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘

ONLINE (Query Time):
┌─────────────────────────────────────────────────────────────┐
│  1. Query Embedding                                         │
│     Input: "machine learning"                               │
│     ↓                                                        │
│     SentenceTransformer.encode()                            │
│     ↓                                                        │
│     Output: [0.23, -0.45, 0.67, ..., 0.12] (768-dim)       │
│                                                              │
│  2. Parallel Search                                         │
│     ┌──────────────────┐  ┌──────────────────┐             │
│     │  FAISS Search    │  │   BM25 Search    │             │
│     │  index.search()  │  │  get_scores()    │             │
│     │  k=20            │  │  k=20            │             │
│     └────────┬─────────┘  └────────┬─────────┘             │
│              │                     │                         │
│  3. Fusion                                                  │
│     ┌────────────────────────────────┐                      │
│     │  Reciprocal Rank Fusion        │                      │
│     │  score = 0.6/(60+r_sem) +      │                      │
│     │          0.4/(60+r_kw)         │                      │
│     └────────────┬───────────────────┘                      │
│                  │                                           │
│  4. Re-ranking & Filtering                                  │
│     ┌────────────────────────────────┐                      │
│     │  - Sort by fused score         │                      │
│     │  - Apply min_score threshold   │                      │
│     │  - Remove duplicates           │                      │
│     │  - Top-K selection             │                      │
│     └────────────┬───────────────────┘                      │
│                  │                                           │
│  5. Output                                                  │
│     Top-5 most relevant articles                            │
└─────────────────────────────────────────────────────────────┘
```

## 7. Deployment Architecture (Planificat)

```
┌──────────────────────────────────────────────────────────────┐
│                      PRODUCTION DEPLOYMENT                    │
└──────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │   GitHub    │
                    │  Repository │
                    └──────┬──────┘
                           │
                           │ git push
                           ▼
                    ┌─────────────┐
                    │   GitHub    │
                    │   Actions   │
                    │   (CI/CD)   │
                    └──────┬──────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
                ▼          ▼          ▼
         ┌──────────┐ ┌──────────┐ ┌──────────┐
         │  Tests   │ │  Build   │ │  Deploy  │
         │  pytest  │ │  Docker  │ │  Cloud   │
         └──────────┘ └──────────┘ └──────────┘
                                         │
                                         ▼
                              ┌─────────────────┐
                              │  Cloud Platform │
                              │  (AWS/GCP/Azure)│
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │ Load Balancer│  │   Database   │  │    Cache     │
            │    (Nginx)   │  │   (SQLite/   │  │   (Redis)    │
            │              │  │  PostgreSQL) │  │              │
            └──────┬───────┘  └──────────────┘  └──────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ Flask  │ │ Flask  │ │ Flask  │
   │Instance│ │Instance│ │Instance│
   │   #1   │ │   #2   │ │   #3   │
   └────────┘ └────────┘ └────────┘
```

## 8. Metrici de Performanță

```
┌──────────────────────────────────────────────────────────────┐
│                  Performance Metrics                          │
└──────────────────────────────────────────────────────────────┘

Component Latency (ms):
┌────────────────────────┬──────────┬──────────┬──────────┐
│ Component              │   Min    │   Avg    │   Max    │
├────────────────────────┼──────────┼──────────┼──────────┤
│ Semantic Search (FAISS)│    10    │    25    │    50    │
│ Keyword Search (BM25)  │     5    │    15    │    30    │
│ Academic API           │   200    │   500    │  1500    │
│ Web Search (DDG)       │   300    │   800    │  2000    │
│ Hybrid Ranking         │     2    │     5    │    10    │
│ Content Verification   │    10    │    20    │    40    │
├────────────────────────┼──────────┼──────────┼──────────┤
│ TOTAL (Parallel)       │   320    │   850    │  2100    │
└────────────────────────┴──────────┴──────────┴──────────┘

Throughput:
- Requests/second: ~50 (single instance)
- Concurrent users: ~100 (with proper scaling)

Storage:
- FAISS Index: ~50MB (10,000 articles)
- BM25 Index: ~10MB
- SQLite DBs: ~20MB
- Embedding Model: ~420MB
```

Aceste diagrame pot fi incluse în documentația de licență pentru a ilustra arhitectura și fluxurile de date!

---

## 9. Diagrame PlantUML

Pentru o calitate superioară de imprimare și scalabilitate, am creat și diagrame PlantUML în directorul `theory_files/plantuml_diagrams/`:

### Diagrame Disponibile

**Versiuni Simplificate (Optimizate pentru A4):**
- `class-diagram-simple.puml` - Modelul de date principal
- `sequence-diagram-simple.puml` - Fluxul de recomandare
- `deployment-diagram-simple.puml` - Arhitectura de deployment
- `activity-diagram-simple.puml` - Pipeline-ul de ingestion
- `state-diagram-simple.puml` - State machine pentru query

**Versiuni Complete (Detaliate):**
- `component-diagram.puml` - Arhitectura componentelor
- `class-diagram.puml` - Toate clasele și relațiile
- `sequence-diagram-recommend.puml` - Fluxul complet de recomandare
- `sequence-diagram-feedback.puml` - Fluxul de feedback
- `deployment-diagram.puml` - Deployment detaliat
- `activity-diagram-ingestion.puml` - Ingestion complet
- `state-diagram-query.puml` - State machine detaliat

### Cum să Generezi Diagramele

Vezi `DIAGRAME_PLANTUML_README.md` pentru instrucțiuni complete.

**Quick Start:**
```bash
# Instalează PlantUML
choco install plantuml  # Windows
brew install plantuml   # Mac

# Navighează la directorul cu diagrame
cd theory_files/plantuml_diagrams

# Generează toate diagramele ca PNG
plantuml *.puml

# Generează ca PDF (recomandat pentru imprimare)
plantuml -tpdf *-simple.puml
```

**Online (fără instalare):**
1. Deschide [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
2. Copiază conținutul fișierului `.puml` din `theory_files/plantuml_diagrams/`
3. Descarcă ca PNG/SVG/PDF

### Recomandări pentru Licență

Pentru o lucrare de licență pe A4, folosește versiunile simplificate:
1. **component-diagram.puml** - Arhitectura generală
2. **sequence-diagram-simple.puml** - Fluxul principal
3. **class-diagram-simple.puml** - Modelul de date
4. **deployment-diagram-simple.puml** - Deployment

Toate se încadrează perfect pe A4 portrait!
