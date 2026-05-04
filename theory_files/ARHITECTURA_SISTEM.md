# Arhitectura Sistemului - Hybrid Thesis Recommender

## 1. Prezentare Generală

Hybrid Thesis Recommender este un sistem de recomandare academic care combină căutarea semantică (FAISS), potrivirea cuvintelor cheie (BM25) și căutarea web live pentru a oferi resurse relevante pentru cercetare. Sistemul este construit pe o arhitectură modulară, scalabilă și bilingvă (română/engleză).

---

## 2. Arhitectura de Nivel Înalt

### 2.1 Diagrama Arhitecturală Generală

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Browser Web<br/>HTML/CSS/JavaScript]
    end

    subgraph "Application Layer"
        Flask[Flask Application<br/>REST API]
        LD[Language Detector]
        Auth[Authentication<br/>Module]
    end

    subgraph "Retrieval Layer"
        SR[Semantic Retriever<br/>FAISS + Embeddings]
        KR[Keyword Retriever<br/>BM25]
        WR[Web Retriever<br/>DuckDuckGo/Google/Bing]
        AR[Academic Retriever<br/>Semantic Scholar/arXiv]
    end

    subgraph "Processing Layer"
        HR[Hybrid Ranker<br/>RRF Fusion]
        CV[Content Verifier<br/>Clickbait Filter]
        FS[Feedback Signal<br/>Rating Boost]
    end

    subgraph "Data Layer"
        FAISS[(FAISS Index<br/>Vector Store)]
        BM25[(BM25 Index<br/>Inverted Index)]
        ArticleDB[(Articles DB<br/>SQLite)]
        FeedbackDB[(Feedback DB<br/>SQLite)]
        UserDB[(Users DB<br/>SQLite)]
    end

    subgraph "External Services"
        WebAPI[Web Search APIs]
        AcademicAPI[Academic APIs]
    end

    Browser -->|HTTP/JSON| Flask
    Flask --> LD
    Flask --> Auth
    Flask --> SR
    Flask --> KR
    Flask --> WR
    Flask --> AR
    
    SR --> FAISS
    SR --> ArticleDB
    KR --> BM25
    KR --> ArticleDB
    WR --> WebAPI
    AR --> AcademicAPI
    
    SR --> HR
    KR --> HR
    WR --> HR
    AR --> HR
    
    HR --> CV
    HR --> FS
    FS --> FeedbackDB
    
    CV --> Browser
    Auth --> UserDB
    
    style Browser fill:#e1f5ff
    style Flask fill:#fff4e1
    style SR fill:#e8f5e9
    style KR fill:#e8f5e9
    style WR fill:#e8f5e9
    style AR fill:#e8f5e9
    style HR fill:#fff3e0
    style CV fill:#fff3e0
    style FAISS fill:#f3e5f5
    style BM25 fill:#f3e5f5
    style ArticleDB fill:#f3e5f5
    style FeedbackDB fill:#f3e5f5
    style UserDB fill:#f3e5f5
```

---

## 3. Arhitectura pe Straturi (Layered Architecture)

### 3.1 Diagrama Straturilor

```mermaid
graph TD
    subgraph "Layer 1: Presentation"
        UI[Web UI<br/>Static HTML/CSS/JS]
        UI_Features[• Form submission<br/>• Result rendering<br/>• Language toggle<br/>• Star ratings<br/>• Dark mode]
    end

    subgraph "Layer 2: API Gateway"
        API[REST API Endpoints]
        Routes[• POST /recommend<br/>• POST /feedback<br/>• GET /feedback/:id<br/>• POST /auth/register<br/>• POST /auth/login<br/>• GET /saved]
    end

    subgraph "Layer 3: Business Logic"
        Orchestrator[Request Orchestrator]
        Validator[Input Validator]
        Serializer[Response Serializer]
    end

    subgraph "Layer 4: Retrieval Services"
        Semantic[Semantic Search]
        Keyword[Keyword Search]
        Web[Web Search]
        Academic[Academic Search]
    end

    subgraph "Layer 5: Processing Services"
        Ranker[Hybrid Ranking]
        Verifier[Content Verification]
        Feedback[Feedback Processing]
    end

    subgraph "Layer 6: Data Access"
        VectorStore[Vector Store Access]
        IndexStore[Index Store Access]
        DBAccess[Database Access]
    end

    subgraph "Layer 7: Storage"
        Storage[• FAISS Index<br/>• BM25 Index<br/>• SQLite DBs<br/>• Config Files]
    end

    UI --> API
    API --> Orchestrator
    Orchestrator --> Validator
    Orchestrator --> Semantic
    Orchestrator --> Keyword
    Orchestrator --> Web
    Orchestrator --> Academic
    
    Semantic --> Ranker
    Keyword --> Ranker
    Web --> Ranker
    Academic --> Ranker
    
    Ranker --> Verifier
    Verifier --> Feedback
    Feedback --> Serializer
    Serializer --> API
    
    Semantic --> VectorStore
    Keyword --> IndexStore
    Ranker --> DBAccess
    Feedback --> DBAccess
    
    VectorStore --> Storage
    IndexStore --> Storage
    DBAccess --> Storage
```

---

## 4. Arhitectura Componentelor

### 4.1 Diagrama Componentelor Detaliate

```mermaid
graph TB
    subgraph "Frontend Components"
        HTML[index.html<br/>UI Structure]
        CSS[style.css<br/>Styling + Dark Mode]
        JS[app.js<br/>Client Logic]
    end

    subgraph "Backend Components"
        Main[main.py<br/>Entry Point]
        API_Module[api.py<br/>Flask App Factory]
        Config[config_manager.py<br/>Hot-reload Config]
        I18N[i18n.py<br/>Localization]
    end

    subgraph "Retrieval Components"
        SemanticRet[semantic.py<br/>Sentence Transformers]
        KeywordRet[keyword.py<br/>BM25 Ranking]
        WebRet[web.py<br/>Web Search]
        AcademicRet[academic_web.py<br/>Scholar/arXiv]
    end

    subgraph "Ranking Components"
        HybridRank[hybrid.py<br/>RRF/Weighted Fusion]
    end

    subgraph "Verification Components"
        ContentVer[content.py<br/>Clickbait Detection]
    end

    subgraph "Storage Components"
        ArticleStore[article_store.py<br/>FAISS + SQLite]
        FeedbackStore[feedback/store.py<br/>Ratings DB]
        UserStore[auth/user_store.py<br/>Users DB]
    end

    subgraph "Ingestion Components"
        Pipeline[ingestion/pipeline.py<br/>JSON/CSV/BibTeX]
    end

    subgraph "Utility Components"
        LangDetect[language_detector.py<br/>langdetect + langid]
        Models[models.py<br/>Data Classes]
    end

    HTML --> JS
    CSS --> JS
    JS --> API_Module
    
    Main --> API_Module
    Main --> Config
    API_Module --> I18N
    API_Module --> LangDetect
    
    API_Module --> SemanticRet
    API_Module --> KeywordRet
    API_Module --> WebRet
    API_Module --> AcademicRet
    
    SemanticRet --> HybridRank
    KeywordRet --> HybridRank
    WebRet --> HybridRank
    AcademicRet --> HybridRank
    
    HybridRank --> ContentVer
    ContentVer --> FeedbackStore
    
    SemanticRet --> ArticleStore
    KeywordRet --> ArticleStore
    API_Module --> UserStore
    
    Pipeline --> ArticleStore
    
    Models --> SemanticRet
    Models --> KeywordRet
    Models --> HybridRank
```

---

## 5. Fluxul de Date (Data Flow)

### 5.1 Fluxul unei Cereri de Recomandare

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Flask API
    participant L as Language Detector
    participant S as Semantic Retriever
    participant K as Keyword Retriever
    participant W as Web Retriever
    participant H as Hybrid Ranker
    participant C as Content Verifier
    participant DB as Databases

    U->>B: Introduce titlu teză
    B->>F: POST /recommend {title, abstract, keywords}
    
    F->>F: Validare input (3-500 chars)
    F->>L: detect(query_text)
    L-->>F: query_language (ro/en)
    
    par Retrieval paralel
        F->>S: retrieve(query, top_k=20)
        S->>DB: FAISS vector search
        DB-->>S: top-20 articles + scores
        S-->>F: semantic_results
    and
        F->>K: retrieve(query, top_k=20)
        K->>DB: BM25 keyword search
        DB-->>K: top-20 articles + scores
        K-->>F: keyword_results
    and
        F->>W: retrieve(query, language)
        W->>W: DuckDuckGo API call
        W-->>F: web_results
    end
    
    F->>H: fuse(semantic, keyword, web)
    H->>H: RRF scoring + deduplication
    H->>DB: get_ratings(item_ids)
    DB-->>H: feedback signals
    H->>H: apply feedback boost
    H-->>F: ranked_articles + ranked_web
    
    F->>C: verify(articles, web, query_emb)
    C->>C: compute title/content similarity
    C->>C: flag clickbait (threshold=0.3)
    C->>C: filter blocklisted domains
    C-->>F: verified_results
    
    F->>F: serialize to JSON
    F-->>B: {articles[], web_resources[], notices[]}
    B->>B: render result cards
    B-->>U: Display results
```

### 5.2 Fluxul Feedback-ului

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Flask API
    participant FS as Feedback Store
    participant DB as SQLite DB

    U->>B: Click pe stea (rating 1-5)
    B->>F: POST /feedback {item_id, query, rating, session_id}
    
    F->>F: Validate rating ∈ [1,5]
    F->>FS: upsert_rating(item_id, rating, session_id)
    FS->>DB: INSERT OR REPLACE INTO ratings
    DB-->>FS: OK
    FS-->>F: Success
    
    F-->>B: {message: "Rating saved."}
    B-->>U: Update UI (star filled)
    
    Note over B,DB: Fetch aggregate ratings
    B->>F: GET /feedback/{item_id}?session_id=...
    F->>FS: get_ratings(item_id, session_id)
    FS->>DB: SELECT AVG(rating), COUNT(*)
    DB-->>FS: {user_rating, avg_rating, count}
    FS-->>F: FeedbackQueryResult
    F-->>B: {user_rating: 4, average: 3.7, count: 12}
    B-->>U: Display "★★★★☆ (12 ratings)"
```

---

## 6. Arhitectura Bazei de Date

### 6.1 Schema Bazei de Date

```mermaid
erDiagram
    ARTICLES {
        TEXT id PK
        TEXT title
        TEXT abstract
        TEXT authors
        INTEGER year
        TEXT doi
        TEXT url
        TEXT keywords
        TEXT language
    }
    
    RATINGS {
        TEXT item_id FK
        TEXT session_id
        TEXT query
        INTEGER rating
        TIMESTAMP updated_at
    }
    
    USERS {
        INTEGER id PK
        TEXT username UK
        TEXT email UK
        TEXT password_hash
        TIMESTAMP created_at
    }
    
    SAVED_ITEMS {
        INTEGER id PK
        INTEGER user_id FK
        TEXT item_id
        TEXT item_data
        TIMESTAMP saved_at
    }
    
    FAISS_INDEX {
        INTEGER article_id
        BLOB embedding_vector
    }
    
    BM25_INDEX {
        TEXT term
        TEXT article_id
        FLOAT tf_idf_score
    }
    
    ARTICLES ||--o{ RATINGS : "rated by users"
    USERS ||--o{ SAVED_ITEMS : "saves"
    ARTICLES ||--|| FAISS_INDEX : "has embedding"
    ARTICLES ||--o{ BM25_INDEX : "indexed by terms"
```

### 6.2 Structura Fișierelor de Date

```
data/
├── articles.db          # SQLite: metadata articole
├── faiss.index          # FAISS: vector embeddings (768-dim)
├── bm25.pkl            # Pickle: BM25 inverted index
├── feedback.db         # SQLite: user ratings
└── users.db            # SQLite: user accounts + saved items
```

---

## 7. Arhitectura de Deployment

### 7.1 Diagrama de Deployment

```mermaid
graph TB
    subgraph "Client Tier"
        Browser[Web Browser<br/>Chrome/Firefox/Safari]
    end

    subgraph "Application Tier"
        subgraph "Flask Server"
            App[Flask Application<br/>Port 5000]
            Static[Static File Server<br/>HTML/CSS/JS]
        end
        
        subgraph "ML Models"
            Transformer[Sentence Transformer<br/>paraphrase-multilingual-mpnet-base-v2]
            FAISS_Lib[FAISS Library<br/>Vector Search]
            BM25_Lib[BM25 Library<br/>rank_bm25]
        end
    end

    subgraph "Data Tier"
        subgraph "Local Storage"
            VectorDB[FAISS Index<br/>~500MB]
            InvertedIdx[BM25 Index<br/>~50MB]
            SQLite[SQLite Databases<br/>~100MB]
        end
    end

    subgraph "External Tier"
        DuckDuckGo[DuckDuckGo API]
        GoogleCSE[Google Custom Search]
        BingAPI[Bing Search API]
        SemanticScholar[Semantic Scholar API]
        ArXiv[arXiv API]
    end

    Browser -->|HTTPS| App
    App --> Static
    App --> Transformer
    App --> FAISS_Lib
    App --> BM25_Lib
    
    FAISS_Lib --> VectorDB
    BM25_Lib --> InvertedIdx
    App --> SQLite
    
    App -->|REST API| DuckDuckGo
    App -->|REST API| GoogleCSE
    App -->|REST API| BingAPI
    App -->|REST API| SemanticScholar
    App -->|REST API| ArXiv
    
    style Browser fill:#e1f5ff
    style App fill:#fff4e1
    style Transformer fill:#e8f5e9
    style VectorDB fill:#f3e5f5
    style DuckDuckGo fill:#ffe0b2
```

### 7.2 Deployment cu Docker (Opțional)

```mermaid
graph TB
    subgraph "Docker Container"
        subgraph "Application"
            Flask[Flask App<br/>Python 3.10]
            Gunicorn[Gunicorn WSGI<br/>4 workers]
        end
        
        subgraph "Dependencies"
            PyTorch[PyTorch<br/>sentence-transformers]
            FAISS_Docker[FAISS-CPU]
            SQLite_Docker[SQLite3]
        end
        
        subgraph "Volumes"
            DataVol[/data<br/>Persistent Volume]
            ConfigVol[/config<br/>Config Files]
        end
    end

    subgraph "Host Machine"
        Port[Port 5000:5000]
        HostData[./data/]
        HostConfig[./config.yaml]
    end

    Gunicorn --> Flask
    Flask --> PyTorch
    Flask --> FAISS_Docker
    Flask --> SQLite_Docker
    
    Flask --> DataVol
    Flask --> ConfigVol
    
    Port --> Gunicorn
    HostData -.->|mount| DataVol
    HostConfig -.->|mount| ConfigVol
```

---

## 8. Arhitectura de Securitate

### 8.1 Diagrama Securității

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Layer 1: Input Validation"
            InputVal[• Query length: 3-500 chars<br/>• Rating range: 1-5<br/>• SQL injection prevention<br/>• XSS sanitization]
        end
        
        subgraph "Layer 2: Authentication"
            Auth[• Session-based auth<br/>• Password hashing (bcrypt)<br/>• CSRF protection<br/>• Secure cookies]
        end
        
        subgraph "Layer 3: Authorization"
            Authz[• User-specific saved items<br/>• Session validation<br/>• Rate limiting<br/>• API key management]
        end
        
        subgraph "Layer 4: Data Protection"
            DataProt[• SQLite file permissions<br/>• Config file encryption<br/>• API key storage<br/>• No sensitive data in logs]
        end
        
        subgraph "Layer 5: External API Security"
            ExtSec[• HTTPS only<br/>• API key rotation<br/>• Request timeouts<br/>• Error handling]
        end
    end

    InputVal --> Auth
    Auth --> Authz
    Authz --> DataProt
    DataProt --> ExtSec
```

---

## 9. Arhitectura de Scalabilitate

### 9.1 Puncte de Scalare

```mermaid
graph LR
    subgraph "Current Architecture"
        Single[Single Flask Instance<br/>In-Memory FAISS<br/>SQLite]
    end

    subgraph "Scaled Architecture"
        LB[Load Balancer<br/>nginx/HAProxy]
        
        subgraph "Application Tier"
            App1[Flask Instance 1]
            App2[Flask Instance 2]
            App3[Flask Instance N]
        end
        
        subgraph "Cache Layer"
            Redis[Redis Cache<br/>Query Results]
        end
        
        subgraph "Data Tier"
            FAISS_Cluster[FAISS Cluster<br/>Distributed Index]
            PostgreSQL[PostgreSQL<br/>Metadata + Ratings]
        end
    end

    Single -.->|Scale Up| LB
    LB --> App1
    LB --> App2
    LB --> App3
    
    App1 --> Redis
    App2 --> Redis
    App3 --> Redis
    
    App1 --> FAISS_Cluster
    App2 --> FAISS_Cluster
    App3 --> FAISS_Cluster
    
    App1 --> PostgreSQL
    App2 --> PostgreSQL
    App3 --> PostgreSQL
```

---

## 10. Arhitectura de Configurare

### 10.1 Managementul Configurației

```mermaid
graph TB
    subgraph "Configuration Sources"
        YAML[config.yaml<br/>Main Config]
        ENV[Environment Variables<br/>.env]
        CLI[CLI Arguments<br/>--port, --debug]
    end

    subgraph "Config Manager"
        Loader[Config Loader]
        Validator[Config Validator]
        Watcher[File Watcher<br/>watchdog]
    end

    subgraph "Application Components"
        Retrievers[Retrievers<br/>weights, top-k]
        Models[ML Models<br/>model names]
        APIs[External APIs<br/>credentials]
        Server[Flask Server<br/>host, port]
    end

    YAML --> Loader
    ENV --> Loader
    CLI --> Loader
    
    Loader --> Validator
    Validator --> Watcher
    
    Watcher -->|hot-reload| Retrievers
    Watcher -->|hot-reload| Models
    Watcher -->|hot-reload| APIs
    Watcher -->|restart required| Server
```

### 10.2 Parametri de Configurare

```yaml
# Retrieval Configuration
semantic_weight: 0.6          # Semantic vs keyword balance
keyword_weight: 0.4
article_top_k: 10             # Max articles returned
web_top_k: 10                 # Max web resources returned
min_article_score: 0.1        # Minimum relevance threshold
min_web_score: 0.05

# Model Configuration
embedding_model: "paraphrase-multilingual-mpnet-base-v2"
vector_store_path: "data/faiss.index"
bm25_index_path: "data/bm25.pkl"

# Web Search Configuration
web_search_provider: "duckduckgo"  # duckduckgo | google_cse | bing
web_search_num_results: 50
bilingual_web_search: false

# Content Verification
mismatch_threshold: 0.3       # Clickbait detection threshold
domain_blocklist: []          # Blocked domains

# Feedback Configuration
feedback_signal_enabled: false
feedback_signal_boost: 0.1
feedback_signal_min_rating: 4.0

# Performance
request_timeout_seconds: 20.0
component_timeout_seconds: 18.0
fusion_strategy: "rrf"        # rrf | weighted_sum
```

---

## 11. Metrici și Monitorizare

### 11.1 Arhitectura de Monitorizare

```mermaid
graph TB
    subgraph "Application Metrics"
        ReqMetrics[Request Metrics<br/>• Response time<br/>• Success rate<br/>• Error rate]
        
        RetMetrics[Retrieval Metrics<br/>• Semantic latency<br/>• Keyword latency<br/>• Web API latency]
        
        QualityMetrics[Quality Metrics<br/>• Clickbait detection rate<br/>• Average relevance score<br/>• User ratings]
    end

    subgraph "System Metrics"
        CPUMem[CPU & Memory<br/>• CPU usage<br/>• Memory usage<br/>• Disk I/O]
        
        ModelMetrics[Model Metrics<br/>• Embedding time<br/>• FAISS search time<br/>• BM25 search time]
    end

    subgraph "Business Metrics"
        UserMetrics[User Metrics<br/>• Active users<br/>• Queries per user<br/>• Saved items]
        
        FeedbackMetrics[Feedback Metrics<br/>• Rating distribution<br/>• Average rating<br/>• Feedback rate]
    end

    subgraph "Logging & Alerting"
        Logs[Application Logs<br/>Python logging]
        Alerts[Alerts<br/>• High error rate<br/>• Slow response<br/>• API failures]
    end

    ReqMetrics --> Logs
    RetMetrics --> Logs
    QualityMetrics --> Logs
    CPUMem --> Logs
    ModelMetrics --> Logs
    UserMetrics --> Logs
    FeedbackMetrics --> Logs
    
    Logs --> Alerts
```

---

## 12. Rezumat Arhitectural

### 12.1 Caracteristici Cheie

| Aspect | Detalii |
|--------|---------|
| **Stil Arhitectural** | Layered Architecture + Microservices-ready |
| **Pattern-uri** | Repository, Factory, Strategy, Observer |
| **Scalabilitate** | Vertical (current), Horizontal (planned) |
| **Disponibilitate** | Single instance (current), HA (planned) |
| **Performanță** | <5s response time, parallel retrieval |
| **Securitate** | Input validation, session auth, HTTPS |
| **Mentenabilitate** | Modular, hot-reload config, comprehensive logging |

### 12.2 Tehnologii Utilizate

| Layer | Tehnologii |
|-------|------------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Flask 3.1.1, Python 3.10+ |
| **ML/AI** | sentence-transformers, FAISS, BM25 |
| **Storage** | SQLite, FAISS index, Pickle |
| **External APIs** | DuckDuckGo, Google CSE, Bing, Semantic Scholar, arXiv |
| **Testing** | pytest, hypothesis (property-based testing) |
| **Config** | PyYAML, watchdog (hot-reload) |

---

## 13. Evoluție Viitoare

### 13.1 Roadmap Arhitectural

```mermaid
timeline
    title Evoluția Arhitecturii
    section Phase 1 (Current)
        Monolithic Flask App : Single instance
        SQLite databases : Local storage
        In-memory FAISS : No distribution
    section Phase 2 (Q2 2026)
        Load Balancing : nginx/HAProxy
        Redis Caching : Query result cache
        PostgreSQL : Centralized DB
    section Phase 3 (Q3 2026)
        Microservices : Separate retrieval services
        Message Queue : RabbitMQ/Kafka
        Distributed FAISS : Cluster deployment
    section Phase 4 (Q4 2026)
        Kubernetes : Container orchestration
        Elasticsearch : Full-text search
        GraphQL API : Flexible queries
```

---

## Concluzie

Arhitectura Hybrid Thesis Recommender este proiectată pentru:
- ✅ **Modularitate**: Componente independente, ușor de testat și înlocuit
- ✅ **Scalabilitate**: Pregătită pentru creștere orizontală
- ✅ **Performanță**: Retrieval paralel, caching, optimizări
- ✅ **Mentenabilitate**: Cod curat, documentație, logging
- ✅ **Extensibilitate**: Ușor de adăugat noi retrievers, rankers, verificatori

Sistemul este construit pe principii solide de inginerie software și este pregătit pentru evoluție continuă.
