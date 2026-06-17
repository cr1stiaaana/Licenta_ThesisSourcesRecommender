# Specificații — Hybrid Thesis Recommender

## 1. Prezentare Generală

Proiectul folosește **trei niveluri de specificații** care ghidează întreaga dezvoltare:

```
┌────────────────────────────────────────────────────────────┐
│  requirements.md  │  CE trebuie să facă sistemul           │
├────────────────────────────────────────────────────────────┤
│  design.md        │  CUM funcționează tehnic               │
├────────────────────────────────────────────────────────────┤
│  tasks.md         │  PAȘI concreți de implementare         │
├────────────────────────────────────────────────────────────┤
│  openapi.yaml     │  CONTRACT API (interfața externă)      │
└────────────────────────────────────────────────────────────┘
```

Locație: `.kiro/specs/hybrid-thesis-recommender/`

---

## 2. Requirements — Cerințe Funcționale

### 2.1 Structură

Fișierul `requirements.md` conține **12 cerințe** formulate ca user stories cu acceptance criteria:

| # | Cerință | User Story |
|---|---------|-----------|
| 1 | Query Input & Validation | Utilizatorul trimite un titlu de teză și primește recomandări |
| 2 | Semantic Retrieval | Sistemul înțelege sensul titlului, nu doar cuvintele |
| 3 | Keyword Retrieval | Sistemul găsește articole cu termeni exacți |
| 4 | Hybrid Ranking & Fusion | Rezultatele din ambii retrieveri sunt combinate optim |
| 5 | Recommendation Output | Fiecare recomandare include metadata suficientă |
| 5b | Content Quality Filtering | Detectare clickbait și surse de calitate scăzută |
| 6 | Web Resource Retrieval | Căutare live pe web pentru resurse non-academice |
| 7 | Article Ingestion | Operatorul poate încărca articole în sistem |
| 8 | Configuration & Tunability | Parametrii sunt configurabili fără restart |
| 9 | Error Handling & Resilience | Sistemul funcționează chiar dacă componente eșuează |
| 10 | Multilingual Support | Suport bilingv RO/EN transparent |
| 11 | Web Application Interface | Interfață web accesibilă din browser |
| 12 | User Feedback | Rating 1-5 stele cu persistență |

### 2.2 Format Acceptance Criteria

Fiecare cerință folosește limbaj formal cu cuvinte cheie:
- **SHALL** — obligatoriu (must)
- **WHEN** — condiție de declanșare
- **WHERE** — condiție contextuală
- **IF...THEN** — comportament condițional

**Exemplu real (Requirement 4 — Hybrid Ranking):**

```
1. WHEN results are available from both the Semantic_Retriever and the 
   Keyword_Retriever, THE Hybrid_Ranker SHALL merge the two result sets 
   using a weighted fusion strategy.

2. THE Hybrid_Ranker SHALL produce a single ranked list of unique Articles 
   ordered by descending combined Score.

3. WHERE only one retriever returns results, THE Hybrid_Ranker SHALL rank 
   and return the available results without error.

4. THE Hybrid_Ranker SHALL deduplicate Articles that appear in both result 
   sets, retaining the higher combined Score.

5. THE System SHALL return at most Top-K Recommendations, where Top-K is 
   configurable and defaults to 10.
```

### 2.3 Glosar de Termeni

Requirements-ul definește un glosar cu 30+ termeni pentru a elimina ambiguitatea:

| Termen | Definiție |
|--------|-----------|
| **Query** | Input-ul utilizatorului (titlu + opțional abstract + keywords) |
| **Article** | Articol academic din corpus (titlu, abstract, autori, DOI) |
| **Web_Resource** | Pagină web găsită live (blog, documentație, tutorial) |
| **Embedding** | Vector 768-dimensional care codifică sensul textului |
| **Hybrid_Ranker** | Componenta care fuzionează rezultatele din mai mulți retrieveri |
| **Score** | Valoare numerică [0.0, 1.0] indicând relevanța |
| **Quality_Score** | Scor secundar care penalizează clickbait |
| **Domain_Blocklist** | Lista de domenii blocate (content farms) |
| **Feedback_Signal** | Rating-uri agregate care influențează ranking-ul viitor |

### 2.4 Proprietăți de Corectitudine

Cerințele definesc **invarianți** care trebuie să fie adevărați pentru ORICE input:

```
P1: ∀ result ∈ results: 0 ≤ result.score ≤ 1.0
P2: results sunt sortate descrescător după scor
P3: Nu există duplicate (∀ i ≠ j: results[i].id ≠ results[j].id)
P4: |results| ≤ Top-K
P5: quality_warning setat ⟺ (title_sim - content_sim) > threshold
P6: Niciun item din domain_blocklist nu apare în output
P7: Upsert idempotent: N rating-uri pentru (item_id, session_id) → 1 record
```

Aceste proprietăți devin **teste automate** cu Hypothesis (property-based testing).

---

## 3. Design — Arhitectură Tehnică

### 3.1 Ce Conține

Fișierul `design.md` traduce cerințele în soluții tehnice:

- **Diagrame Mermaid** — sequence diagram (request flow), component diagram, flowchart complet
- **Algoritmi detaliați** — BM25, RRF, cosine similarity, content verification, feedback boost
- **Interfețe Python** — semnături de clase și metode cu pre/post-condiții
- **Modele de date** — dataclasses cu tipuri
- **Decizii tehnologice** — justificări pentru fiecare alegere

### 3.2 Algoritmi Documentați

| Algoritm | Scop | Formula |
|----------|------|---------|
| **Cosine Similarity** | Similaritate semantică | `cos(A,B) = (A·B) / (|A|×|B|)` |
| **BM25** | Keyword matching | `Σ IDF(t) × TF(t,d)×(k1+1) / (TF(t,d) + k1×(1-b+b×|d|/avgdl))` |
| **RRF** | Fuziune ranking | `RRF(d) = Σ weight_r / (60 + rank_r(d))` |
| **Web Score** | Scor din rank | `score(rank) = 1.0 / (rank + 1)` |
| **Quality Score** | Penalizare clickbait | `Q = score × (1 - clamp(title_sim - content_sim, 0, 1))` |
| **Feedback Boost** | Boost din rating-uri | `boosted = score + 0.1 × (avg_rating - 1) / 4` |

### 3.3 Decizii de Design cu Justificări

| Decizie | Alternativă respinsă | Justificare |
|---------|---------------------|-------------|
| RRF peste weighted sum | Weighted score averaging | RRF e scale-free, nu necesită calibrare scoruri |
| FAISS IndexFlatIP | ChromaDB, Pinecone | Zero-config, fără server extern, suficient pentru corpus mic-mediu |
| SQLite | PostgreSQL, MongoDB | Embedded, zero-config, ACID, portabil (un fișier) |
| langdetect + langid ensemble | Doar langdetect | Texte scurte sunt greu de clasificat cu un singur model |
| DuckDuckGo default | Google CSE | Gratuit, fără API key, suficient pentru demo |
| `paraphrase-multilingual-mpnet-base-v2` | `all-MiniLM-L6-v2` | Suport nativ RO+EN, cross-lingual |

### 3.4 Interfețe Documentate

Fiecare componentă are interfața definită în design:

```python
class SemanticRetriever:
    def retrieve(self, query: Query, top_k: int) -> RetrievalResult:
        """Encode query, search FAISS, return top-k with scores in [0,1]."""

class KeywordRetriever:
    def retrieve(self, query: Query, top_k: int) -> RetrievalResult:
        """Tokenize query, run BM25, normalize scores to [0,1]."""

class HybridRanker:
    def fuse_articles(self, semantic, keyword, top_k, weights) -> list[ArticleRecommendation]:
        """RRF fusion + dedup + feedback boost + min_score filter."""

class ContentVerifier:
    def verify(self, articles, web_resources, query_embedding, language, config):
        """Clickbait detection + domain blocklist. No HTTP requests."""
```

---

## 4. Tasks — Plan de Implementare

### 4.1 Structură

Fișierul `tasks.md` conține **19 task-uri** ordonate cronologic:

```
Task 1:  Project scaffold + config layer
Task 2:  Data models
Task 3:  Language detection
Task 4:  Article store + ingestion pipeline
Task 5:  Semantic retriever
Task 6:  Keyword retriever
Task 7:  ★ CHECKPOINT — core retrievers working
Task 8:  Web retriever + search adapters
Task 9:  Hybrid ranker
Task 10: Content verifier
Task 11: ★ CHECKPOINT — retrieval pipeline complete
Task 12: Feedback store
Task 13: Flask REST API
Task 14: ★ CHECKPOINT — backend API complete
Task 15: Frontend (HTML/CSS/JS)
Task 16: Feedback signal boost wiring
Task 17: Multilingual message localization
Task 18: Integration wiring + end-to-end validation
Task 19: ★ CHECKPOINT — full system integration
```

### 4.2 Trasabilitate

Fiecare task referențiază cerințele pe care le implementează:

```markdown
- [x] 9.1 Implement HybridRanker
  - Implement fuse_articles() with RRF
  - Deduplicate by DOI or normalized title
  - Apply feedback signal boost when enabled
  - Apply min_article_score threshold
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
```

### 4.3 Checkpoints

La task-urile 7, 11, 14, 19 se face validare incrementală:
- Toate testele trec
- Componentele se integrează corect
- Se poate demonstra funcționalitate parțială

### 4.4 Status Actual

| Status | Simbol | Semnificație |
|--------|--------|-------------|
| Completat | `[x]` | Implementat și validat |
| În așteptare | `[ ]` | Neînceput |
| Parțial | `[-]` | Început dar incomplet |
| Opțional | `[ ]*` | Poate fi omis pentru MVP |

**Progres**: ~85% completat (task-urile principale implementate, teste opționale rămase).

---

## 5. OpenAPI Specification (`openapi.yaml`)

### 5.1 Ce Este

OpenAPI 3.0.3 este un standard industrial pentru documentarea API-urilor REST. Fișierul `openapi.yaml` definește **contractul** dintre frontend și backend.

### 5.2 Endpoint-uri Documentate

| Endpoint | Metodă | Tag | Descriere |
|----------|--------|-----|-----------|
| `/recommend` | POST | Recommendations | Recomandări hibride |
| `/feedback` | POST | Feedback | Submitere rating |
| `/feedback/{item_id}` | GET | Feedback | Interogare rating-uri |
| `/auth/register` | POST | Authentication | Înregistrare |
| `/auth/login` | POST | Authentication | Autentificare |
| `/auth/logout` | POST | Authentication | Deconectare |
| `/auth/me` | GET | Authentication | User curent |
| `/saved` | GET/POST | Saved Items | Articole salvate |
| `/saved/{item_id}` | DELETE | Saved Items | Ștergere salvare |
| `/saved/{item_id}/check` | GET | Saved Items | Verificare salvare |

### 5.3 Schemas Definite

| Schema | Câmpuri principale |
|--------|-------------------|
| `RecommendResponse` | query_language, articles[], web_resources[], notices[] |
| `ArticleRecommendation` | title, authors, year, abstract_snippet, score, doi, quality_warning |
| `WebResourceRecommendation` | title, url, snippet, web_score, keywords, quality_warning |
| `FeedbackQueryResult` | item_id, user_rating, average_rating, rating_count |
| `UserInfo` | id, username, email |

### 5.4 Validări Specificate

```yaml
title:
  type: string
  minLength: 3
  maxLength: 500

rating:
  type: integer
  minimum: 1
  maximum: 5

username:
  type: string
  minLength: 3

password:
  type: string
  minLength: 6
```

### 5.5 Documentație Generată Automat

Din `openapi.yaml` se generează:
- **Swagger UI** (`docs/swagger-ui.html`) — documentație interactivă cu "Try it out"
- **Redoc** (`docs/redoc.html`) — documentație statică elegantă
- **Markdown** (`docs/api-docs.md`) — documentație lightweight

```bash
python generate_docs.py  # Generează toate cele 3 formate
```

---

## 6. Relația între Specificații

```
requirements.md                    openapi.yaml
     │                                  │
     │  "THE System SHALL accept        │  title:
     │   a Query containing at          │    minLength: 3
     │   minimum a thesis title         │    maxLength: 500
     │   of 3 to 500 characters"        │
     │                                  │
     ▼                                  ▼
design.md                          Contract Tests
     │                                  │
     │  class SemanticRetriever:        │  def test_title_validation():
     │    def retrieve(query, k)        │    assert response.status == 422
     │      → RetrievalResult           │    when title < 3 chars
     │                                  │
     ▼                                  ▼
tasks.md                           Implementation
     │                                  │
     │  [x] 5.1 Implement              │  app/retrievers/semantic.py
     │      SemanticRetriever           │  app/api.py (validation)
     │  _Req: 2.1, 2.2, 2.3_           │
     │                                  │
     ▼                                  ▼
   Code                              Tests
     │                                  │
     │  semantic_retriever.py           │  test_integration.py
     │  keyword_retriever.py            │  test_api_contract.py
     │  hybrid_ranker.py                │  property tests (hypothesis)
```

### 6.1 Trasabilitate Completă

Orice linie de cod poate fi trasată înapoi la o cerință:

```
app/rankers/hybrid.py:_rrf_score()
  ← Task 9.1: "Implement fuse_articles with RRF"
    ← Design: "RRF_score(d) = Σ weight_r / (60 + rank_r(d))"
      ← Requirement 4.1: "THE Hybrid_Ranker SHALL merge using weighted fusion"
        ← User Story: "I want the best results combined into a single ranked list"
```

### 6.2 Validare pe Niveluri

| Nivel | Validat prin |
|-------|-------------|
| Requirements | Review stakeholders, acceptance criteria clare |
| Design | Diagrame, pseudocod, pre/post-condiții |
| Tasks | Checkpoints, teste la fiecare pas |
| OpenAPI | Contract tests, Swagger UI "Try it out" |
| Code | Unit tests, property tests, integration tests |

---

## 7. Contract Testing

Testele de contract verifică că implementarea respectă specificația OpenAPI:

```python
# tests/test_api_contract.py

class TestRecommendContract:
    def test_response_has_required_fields(self, client):
        """Verify response matches RecommendResponse schema."""
        resp = client.post('/recommend', json={"title": "machine learning"})
        data = resp.json
        
        assert "query_language" in data
        assert "articles" in data
        assert "web_resources" in data
        assert data["query_language"] in ("ro", "en")
    
    def test_article_schema(self, client):
        """Verify each article matches ArticleRecommendation schema."""
        resp = client.post('/recommend', json={"title": "neural networks"})
        for article in resp.json["articles"]:
            assert article["resource_type"] == "article"
            assert isinstance(article["title"], str)
            assert isinstance(article["score"], float)
            assert 0.0 <= article["score"] <= 1.0
    
    def test_validation_error_format(self, client):
        """Verify 422 response matches error schema."""
        resp = client.post('/recommend', json={"title": "ab"})
        assert resp.status_code == 422
        assert "error" in resp.json
```

---

## 8. Beneficii ale Abordării cu Specificații

### Pentru Dezvoltare
- **Claritate**: Fiecare componentă știe exact ce trebuie să facă
- **Paralelizare**: Frontend și backend pot fi dezvoltate simultan pe baza contractului OpenAPI
- **Refactoring sigur**: Testele de contract detectează regresii

### Pentru Licență
- **Documentație ready-made**: Requirements și design pot fi incluse direct în lucrare
- **Trasabilitate demonstrabilă**: Comisia vede legătura cerință → cod → test
- **Metodologie clară**: SDD e o metodologie documentabilă

### Pentru Mentenanță
- **Onboarding**: Un dezvoltator nou citește requirements → design → tasks și înțelege tot
- **Extensibilitate**: Adăugarea unui feature nou urmează același flux
- **Debugging**: Când ceva nu merge, trasabilitatea arată unde s-a rupt lanțul

---

## 9. Statistici Specificații

| Metric | Valoare |
|--------|---------|
| Cerințe funcționale | 12 |
| Acceptance criteria totale | ~80 |
| Proprietăți de corectitudine | 8 |
| Componente în design | 10 |
| Algoritmi documentați | 6 |
| Task-uri de implementare | 19 |
| Endpoint-uri API | 10 |
| Schemas OpenAPI | 5 |
| Contract tests | ~23 |
| Completare tasks | ~85% |
