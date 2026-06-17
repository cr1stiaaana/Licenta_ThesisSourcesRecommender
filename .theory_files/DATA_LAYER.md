# Nivelul de Date — Hybrid Thesis Recommender

## 1. Prezentare Generală

Sistemul folosește o arhitectură de stocare **hibridă** care combină:
- **SQLite** — baze de date relaționale embedded (metadata, feedback, utilizatori)
- **FAISS** — index vectorial pentru embeddings (căutare semantică)
- **Pickle** — serializare index BM25 (căutare keyword)

Toate datele sunt stocate local în directorul `data/`:

```
data/
├── articles.db      # Metadata articole (SQLite)
├── faiss.index      # Embeddings vectoriale (FAISS binary)
├── bm25.pkl         # Index BM25 serializat (Pickle)
├── feedback.db      # Rating-uri utilizatori (SQLite)
└── users.db         # Conturi + articole salvate (SQLite)
```

---

## 2. Baze de Date SQLite

### 2.1 De ce SQLite?

| Avantaj | Detaliu |
|---------|---------|
| **Zero-configuration** | Nu necesită server separat, nu are proces daemon |
| **Embedded** | Biblioteca e inclusă direct în Python (modul `sqlite3`) |
| **ACID compliant** | Tranzacții atomice, consistente, izolate, durabile |
| **Portabil** | Un singur fișier per bază de date, copiabil/backupabil trivial |
| **Performant** | Suficient pentru mii de articole și zeci de utilizatori concurenți |
| **Cross-platform** | Funcționează identic pe Windows, Linux, macOS |

**Limitări acceptate:**
- Nu suportă acces concurent masiv (write lock pe întreaga DB)
- Nu are tipuri de date stricte (type affinity, nu enforcement)
- Nu suportă replicare nativă

Pentru un sistem academic cu un singur server și volum moderat, SQLite e alegerea optimă.

---

### 2.2 `articles.db` — Metadata Articole

**Scop**: Stochează informațiile descriptive ale articolelor indexate.

```sql
CREATE TABLE articles (
    id TEXT PRIMARY KEY,          -- SHA-256 hash (DOI sau titlu normalizat)
    title TEXT NOT NULL,          -- Titlul articolului
    abstract TEXT,                -- Abstractul complet
    authors TEXT,                 -- JSON array: ["Autor 1", "Autor 2"]
    year INTEGER,                -- Anul publicării
    doi TEXT,                     -- Digital Object Identifier
    url TEXT,                     -- Link la full text
    keywords TEXT,                -- JSON array: ["keyword1", "keyword2"]
    language TEXT,                -- "ro" sau "en"
    faiss_idx INTEGER             -- Poziția în indexul FAISS
);
```

**Statistici corpus actual:**
- Total articole: **28**
- Limbi: EN (27), RO (1)
- Interval ani: 1996 – 2026
- Tematici: formal specifications, recommender systems, NLP, AI

**Relația cu FAISS:**
- Câmpul `faiss_idx` leagă fiecare articol de poziția sa în indexul vectorial
- La căutare semantică: FAISS returnează `faiss_idx` → lookup în SQLite pentru metadata

**Identificare articole:**
```python
# ID = SHA-256 al DOI-ului (dacă există) sau al titlului normalizat
import hashlib
article_id = hashlib.sha256(doi.encode()).hexdigest()  # dacă DOI disponibil
article_id = hashlib.sha256(title.lower().strip().encode()).hexdigest()  # fallback
```

**Câmpuri JSON:**
- `authors` și `keywords` sunt stocate ca JSON arrays serializate ca text
- La citire: `json.loads(row["authors"])` → `["Autor 1", "Autor 2"]`
- Motivul: SQLite nu are tip nativ array; JSON text e simplu și queryable cu `json_extract()`

---

### 2.3 `feedback.db` — Rating-uri Utilizatori

**Scop**: Persistă evaluările utilizatorilor pentru articole și resurse web.

```sql
CREATE TABLE ratings (
    item_id    TEXT,              -- ID articol sau hash URL resursă web
    session_id TEXT,              -- Identificator sesiune browser
    query      TEXT,              -- Query-ul care a generat recomandarea
    rating     INTEGER,           -- Valoare 1-5 (stele)
    updated_at TIMESTAMP,         -- Ultima actualizare
    UNIQUE(item_id, session_id)   -- Un singur rating per (item, sesiune)
);
```

**Semantică Upsert:**
```sql
INSERT OR REPLACE INTO ratings (item_id, session_id, query, rating, updated_at)
VALUES (?, ?, ?, ?, ?)
```
- Dacă `(item_id, session_id)` există deja → UPDATE
- Dacă nu există → INSERT
- Rezultat: un singur record per pereche, mereu cu ultimul rating

**Interogări tipice:**
```sql
-- Rating-ul unui utilizator specific
SELECT rating FROM ratings WHERE item_id = ? AND session_id = ?

-- Media și count pentru un item
SELECT COUNT(*) AS rating_count, AVG(CAST(rating AS REAL)) AS average_rating
FROM ratings WHERE item_id = ?
```

**Utilizare în Feedback Signal Boost:**
- Când `feedback_signal_enabled = true`, HybridRanker interogează `feedback.db`
- Articolele cu `avg_rating >= 4.0` primesc un boost de scor
- Formula: `boosted = rrf_score + 0.1 × (avg_rating - 1) / 4`

---

### 2.4 `users.db` — Conturi și Articole Salvate

**Scop**: Autentificare utilizatori și persistență articole favorite.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,    -- Min 3 caractere
    email TEXT UNIQUE NOT NULL,       -- Format valid email
    password_hash TEXT NOT NULL,      -- SHA-256 hash al parolei
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE saved_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,         -- FK → users.id
    item_id TEXT NOT NULL,            -- ID articol sau hash URL
    item_data TEXT NOT NULL,          -- JSON complet al articolului/resursei
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, item_id)          -- Un item salvat o singură dată per user
);
```

**Autentificare:**
- Password hashing: SHA-256 (simplificat pentru proiect academic)
- Session management: Flask sessions (cookie-based)
- Notă: în producție s-ar folosi bcrypt sau argon2

**Articole salvate:**
- `item_data` stochează JSON-ul complet al articolului/resursei web
- La ștergere user → CASCADE șterge și saved_items asociate
- Constraint UNIQUE previne salvarea duplicată

---

## 3. FAISS — Index Vectorial

### 3.1 Ce Este FAISS

**FAISS** (Facebook AI Similarity Search) este o bibliotecă pentru căutare eficientă de similaritate în spații vectoriale de dimensiune mare.

### 3.2 Configurare în Proiect

```python
import faiss
import numpy as np

_EMBEDDING_DIM = 768  # Dimensiunea vectorilor (paraphrase-multilingual-mpnet-base-v2)

# Creare index nou
index = faiss.IndexFlatIP(_EMBEDDING_DIM)  # Inner Product (= cosine pe vectori normalizați)

# Adăugare vector
vector = model.encode("text articol")
vector = vector / np.linalg.norm(vector)  # Normalizare L2
index.add(vector.reshape(1, 768))

# Căutare
query_vec = model.encode("query utilizator")
query_vec = query_vec / np.linalg.norm(query_vec)
scores, indices = index.search(query_vec.reshape(1, 768), top_k=10)
```

### 3.3 Tipul de Index: `IndexFlatIP`

| Proprietate | Valoare |
|-------------|---------|
| Tip | Flat (exhaustive search) |
| Metric | Inner Product |
| Dimensiune | 768 |
| Complexitate căutare | O(n) — liniar în nr. vectori |
| Acuratețe | 100% (exact, nu aproximativ) |
| Memorie | ~3KB per vector (768 × 4 bytes float32) |

**De ce Inner Product și nu L2?**
- Vectorii sunt normalizați L2 la adăugare
- Pe vectori normalizați: `inner_product(A, B) = cosine_similarity(A, B)`
- Cosine similarity e metrica standard pentru similaritate semantică text

**De ce Flat și nu IVF/HNSW?**
- Corpus mic (28 articole, scalabil la câteva mii)
- Căutare exactă (nu aproximativă) — important pentru calitate
- Simplitate (nu necesită training/clustering)
- La 1000 articole, căutarea durează <1ms

### 3.4 Persistență

```python
# Salvare pe disc
faiss.write_index(index, "data/faiss.index")

# Încărcare de pe disc
index = faiss.read_index("data/faiss.index")
```

Fișierul `faiss.index` este binar, dimensiune ≈ `n_articles × 768 × 4 bytes`.
- 28 articole → ~84KB
- 1000 articole → ~3MB
- 100.000 articole → ~300MB

### 3.5 Relația FAISS ↔ SQLite

```
┌─────────────────────┐         ┌─────────────────────┐
│   FAISS Index       │         │   articles.db       │
│                     │         │                     │
│  idx=0: [0.12, ...]│◄────────│  faiss_idx=0, id="abc"
│  idx=1: [0.45, ...]│◄────────│  faiss_idx=1, id="def"
│  idx=2: [0.78, ...]│◄────────│  faiss_idx=2, id="ghi"
│  ...               │         │  ...                │
└─────────────────────┘         └─────────────────────┘

Căutare:
1. FAISS search(query_vec, k=10) → [(score=0.87, idx=2), (score=0.72, idx=0), ...]
2. Lookup: faiss_idx_to_id[2] → "ghi"
3. SQLite: SELECT * FROM articles WHERE id = "ghi"
4. Return: Article(title="...", authors=[...], score=0.87)
```

---

## 4. BM25 Index (`bm25.pkl`)

### 4.1 Ce Stochează

Indexul BM25 este un obiect `rank_bm25.BM25Okapi` serializat cu pickle:
- **Vocabular**: toate cuvintele din corpus
- **IDF scores**: inverse document frequency per termen
- **Document lengths**: lungimea fiecărui document (pentru normalizare)
- **Parametri**: k1=1.5, b=0.75

### 4.2 Construcție

```python
from rank_bm25 import BM25Okapi
import pickle

# Corpus = lista de documente tokenizate (în ordinea faiss_idx)
corpus = article_store.get_all_texts()
# corpus = [["hybrid", "recommender", "systems"], ["neural", "networks", ...], ...]

bm25 = BM25Okapi(corpus)

# Serializare
with open("data/bm25.pkl", "wb") as f:
    pickle.dump(bm25, f)
```

### 4.3 Aliniere cu FAISS și SQLite

**Critică**: Ordinea documentelor în BM25 trebuie să corespundă cu `faiss_idx`:
- Document la poziția 0 în BM25 = articolul cu `faiss_idx=0` în SQLite
- Dacă se adaugă articole noi, BM25 trebuie reconstruit (`python rebuild_indexes.py`)

### 4.4 Rebuild

```bash
# După ingestie de articole noi
python rebuild_indexes.py

# Ce face:
# 1. Citește toate articolele din articles.db (ORDER BY faiss_idx)
# 2. Tokenizează fiecare document
# 3. Construiește BM25Okapi nou
# 4. Serializează la data/bm25.pkl
```

---

## 5. Fluxul de Date

### 5.1 Ingestie (Write Path)

```
Fișier JSON/CSV/BibTeX
        │
        ▼
┌─────────────────────┐
│  IngestionPipeline  │
│  - Parse fișier     │
│  - Validare         │
│  - Detect limbă     │
│  - Generare ID      │
└─────────┬───────────┘
          │
          ├──────────────────────────────────┐
          ▼                                  ▼
┌─────────────────────┐         ┌─────────────────────┐
│  articles.db        │         │  faiss.index        │
│  INSERT metadata    │         │  ADD embedding      │
│  (title, authors,   │         │  (768-dim vector)   │
│   abstract, DOI...) │         │                     │
└─────────────────────┘         └─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  bm25.pkl           │
│  REBUILD index      │
│  (tokenized corpus) │
└─────────────────────┘
```

### 5.2 Căutare (Read Path)

```
Query: "machine learning in healthcare"
        │
        ├─── Semantic Path ──────────────────────────────────┐
        │    encode(query) → vector 768-dim                  │
        │    FAISS search(vector, k=20) → [(idx, score)...]  │
        │    SQLite lookup(idx) → Article metadata           │
        │                                                    │
        ├─── Keyword Path ───────────────────────────────────┤
        │    tokenize(query) → ["machine", "learning", ...]  │
        │    BM25.get_scores(tokens) → [0.0, 0.3, 0.8, ...] │
        │    Top-K indices → SQLite lookup → Articles        │
        │                                                    │
        ├─── Web Path ───────────────────────────────────────┤
        │    DuckDuckGo search(query) → Web results          │
        │    (nu accesează baza de date locală)              │
        │                                                    │
        └────────────────────────────────────────────────────┘
                              │
                              ▼
                    HybridRanker (RRF fusion)
                              │
                              ▼
                    ContentVerifier (quality check)
                              │
                              ▼
                    JSON Response → Frontend
```

### 5.3 Feedback (Write + Read)

```
User dă rating 4 stele
        │
        ▼
POST /feedback {item_id, rating, session_id}
        │
        ▼
┌─────────────────────┐
│  feedback.db        │
│  INSERT OR REPLACE  │
│  ratings table      │
└─────────────────────┘

--- La următoarea căutare (dacă feedback_signal_enabled) ---

HybridRanker → SELECT AVG(rating) FROM ratings WHERE item_id = ?
             → Dacă avg >= 4.0: boost scor cu 0.1 × normalized_avg
```

---

## 6. Diagrama Entitate-Relație

```
┌─────────────────────────────────────────────────────────────────┐
│                        articles.db                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ articles                                                  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ PK  id          TEXT (SHA-256)                           │   │
│  │     title       TEXT NOT NULL                            │   │
│  │     abstract    TEXT                                     │   │
│  │     authors     TEXT (JSON array)                        │   │
│  │     year        INTEGER                                  │   │
│  │     doi         TEXT                                     │   │
│  │     url         TEXT                                     │   │
│  │     keywords    TEXT (JSON array)                        │   │
│  │     language    TEXT ("ro" | "en")                       │   │
│  │     faiss_idx   INTEGER ──────────────► FAISS Index      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        feedback.db                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ratings                                                   │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ UK  (item_id, session_id)                                │   │
│  │     item_id     TEXT ─────────────────► articles.id      │   │
│  │     session_id  TEXT                    (sau URL hash)    │   │
│  │     query       TEXT                                     │   │
│  │     rating      INTEGER [1-5]                            │   │
│  │     updated_at  TIMESTAMP                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         users.db                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ users                                                     │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ PK  id            INTEGER AUTOINCREMENT                  │   │
│  │ UK  username      TEXT NOT NULL                          │   │
│  │ UK  email         TEXT NOT NULL                          │   │
│  │     password_hash TEXT NOT NULL                          │   │
│  │     created_at    TIMESTAMP                              │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                          │ 1:N                                   │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │ saved_items                                               │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ PK  id            INTEGER AUTOINCREMENT                  │   │
│  │ FK  user_id       INTEGER → users.id (CASCADE DELETE)    │   │
│  │ UK  (user_id, item_id)                                   │   │
│  │     item_id       TEXT                                   │   │
│  │     item_data     TEXT (JSON complet)                    │   │
│  │     saved_at      TIMESTAMP                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Consistență și Integritate

### 7.1 Constrângeri

| Bază | Constrângere | Scop |
|------|-------------|------|
| articles.db | `id` PRIMARY KEY | Unicitate articole |
| feedback.db | `UNIQUE(item_id, session_id)` | Un rating per (item, sesiune) |
| users.db | `username` UNIQUE | Unicitate username |
| users.db | `email` UNIQUE | Unicitate email |
| users.db | `UNIQUE(user_id, item_id)` | Un item salvat o dată per user |
| users.db | `FOREIGN KEY ... ON DELETE CASCADE` | Ștergere user → ștergere saved_items |

### 7.2 Sincronizare FAISS ↔ SQLite

**Invariant**: `faiss_idx` din SQLite trebuie să corespundă exact cu poziția vectorului în FAISS.

- La `add_article()`: se adaugă simultan în ambele (FAISS + SQLite)
- La update: se reconstruiește vectorul la aceeași poziție
- Mapping-uri in-memory: `_id_to_faiss_idx` și `_faiss_idx_to_id`

### 7.3 Sincronizare BM25 ↔ SQLite

**Invariant**: Ordinea documentelor în BM25 = ordinea `faiss_idx` din SQLite.

- BM25 se construiește cu `SELECT ... ORDER BY faiss_idx`
- După ingestie nouă: `python rebuild_indexes.py` reconstruiește BM25
- Dacă BM25 nu e sincronizat → keyword retriever returnează articole greșite

---

## 8. Operații CRUD

### 8.1 Articles

| Operație | Metodă | Detaliu |
|----------|--------|---------|
| **Create** | `ArticleStore.add_article()` | Upsert (INSERT sau UPDATE pe id) |
| **Read** | `ArticleStore.get_article_by_id()` | Lookup pe PRIMARY KEY |
| **Read** | `ArticleStore.search_vector()` | Căutare semantică via FAISS |
| **Read** | `KeywordRetriever.retrieve()` | Căutare BM25 |
| **Update** | `ArticleStore.add_article()` | Același id → update metadata + vector |
| **Delete** | Nu implementat | Articolele nu se șterg (corpus append-only) |

### 8.2 Feedback

| Operație | Metodă | Detaliu |
|----------|--------|---------|
| **Create/Update** | `FeedbackStore.upsert_rating()` | INSERT OR REPLACE |
| **Read** | `FeedbackStore.get_ratings()` | Agregare AVG + COUNT + user rating |

### 8.3 Users

| Operație | Metodă | Detaliu |
|----------|--------|---------|
| **Create** | `UserStore.create_user()` | INSERT cu validare unicitate |
| **Read** | `UserStore.authenticate()` | SELECT pe username + password_hash |
| **Read** | `UserStore.get_saved_items()` | SELECT saved_items WHERE user_id |
| **Create** | `UserStore.save_item()` | INSERT OR REPLACE saved_items |
| **Delete** | `UserStore.unsave_item()` | DELETE saved_items |

---

## 9. Performanță și Scalabilitate

### 9.1 Dimensiuni Actuale

| Fișier | Dimensiune | Conținut |
|--------|-----------|----------|
| `articles.db` | ~50KB | 28 articole |
| `faiss.index` | ~84KB | 28 vectori × 768 × 4 bytes |
| `bm25.pkl` | ~20KB | Index BM25 pentru 28 documente |
| `feedback.db` | ~12KB | Câteva rating-uri test |
| `users.db` | ~12KB | Câțiva utilizatori test |

### 9.2 Estimări la Scală

| Articole | articles.db | faiss.index | bm25.pkl | Timp căutare |
|----------|-------------|-------------|----------|-------------|
| 100 | ~200KB | ~300KB | ~50KB | <5ms |
| 1.000 | ~2MB | ~3MB | ~500KB | <10ms |
| 10.000 | ~20MB | ~30MB | ~5MB | <50ms |
| 100.000 | ~200MB | ~300MB | ~50MB | <500ms |

### 9.3 Bottleneck-uri

1. **FAISS Flat** — O(n) la căutare. La >100K articole, ar trebui migrat la `IndexIVFFlat` sau `IndexHNSW`
2. **BM25 in-memory** — Încărcat complet în RAM. La >100K, ar trebui migrat la Elasticsearch
3. **SQLite write lock** — Un singur writer la un moment dat. La >10 utilizatori concurenți, ar trebui PostgreSQL

### 9.4 Optimizări Implementate

- **Lazy loading**: FAISS index și BM25 se încarcă o singură dată la startup
- **In-memory mappings**: `_id_to_faiss_idx` evită query SQLite la fiecare căutare
- **check_same_thread=False**: Permite acces SQLite din thread-uri diferite (ThreadPoolExecutor)
- **Batch operations**: Ingestia procesează articole în bulk

---

## 10. Backup și Recovery

### 10.1 Backup

```bash
# Backup complet (toate datele)
cp -r data/ data_backup_$(date +%Y%m%d)/

# Sau individual
cp data/articles.db backup/
cp data/faiss.index backup/
cp data/feedback.db backup/
cp data/users.db backup/
```

### 10.2 Recovery

```bash
# Restaurare din backup
cp backup/articles.db data/
cp backup/faiss.index data/

# Reconstruire BM25 (derivat din articles.db)
python rebuild_indexes.py
```

### 10.3 Ce se poate reconstrui

| Fișier | Reconstituibil? | Din ce |
|--------|:---------------:|--------|
| `articles.db` | ❌ | Sursă primară — trebuie backup |
| `faiss.index` | ✅ | Re-encode toate articolele din articles.db |
| `bm25.pkl` | ✅ | Rebuild din articles.db |
| `feedback.db` | ❌ | Rating-uri utilizatori — trebuie backup |
| `users.db` | ❌ | Conturi — trebuie backup |

---

## 11. Schema PostgreSQL (Planificată)

Pentru deployment în producție, există o schemă PostgreSQL pregătită (`database/schema.sql`) cu:
- Tipuri de date stricte (`VARCHAR`, `JSONB`, `SERIAL`)
- Foreign keys cu `ON DELETE CASCADE`
- Indexuri pe câmpuri frecvent interogate
- Triggers pentru `updated_at` automat
- Comentarii pe tabele

Migrarea de la SQLite la PostgreSQL ar necesita:
1. Export date din SQLite
2. Import în PostgreSQL
3. Actualizare connection strings în `config.yaml`
4. Înlocuire `sqlite3` cu `psycopg2` în store classes
