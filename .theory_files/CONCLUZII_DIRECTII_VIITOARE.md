# Capitolul: Concluzii și Direcții Viitoare

## 1. Concluzii

### 1.1 Metodologia Spec-Driven Development — Evaluare

Proiectul a fost dezvoltat integral folosind **Spec-Driven Development (SDD)** cu workflow-ul Requirements-First, asistat de mediul Kiro. Această abordare a demonstrat următoarele beneficii concrete:

| Aspect | Rezultat |
|--------|----------|
| **Trasabilitate** | Fiecare din cele 19 task-uri de implementare referențiază cerințe specifice din requirements.md |
| **Completitudine** | Toate cele 12 cerințe funcționale au fost implementate și validate |
| **Calitate** | 8 proprietăți de corectitudine formalizate și testate automat cu Hypothesis |
| **Documentație** | Specificațiile servesc simultan ca documentație tehnică — nu e nevoie de documentare separată |
| **Iterare controlată** | Checkpoints la task-urile 7, 11, 14, 19 au permis validare incrementală |
| **Conformitate API** | OpenAPI spec + contract tests (schemathesis) + validare automată în pipeline CI/CD |

**Lecții învățate din aplicarea SDD:**
- Investiția inițială în requirements (definire glosar, acceptance criteria formale) se recuperează prin reducerea ambiguităților în implementare
- Property-based testing transformă cerințele abstracte în verificări executabile automat
- Hot-reload config + specificații externalizate permit ajustare fără recompilare
- Trasabilitatea bidirecțională (cerință → cod, cod → cerință) simplifică debugging-ul și mentenanța

**Limitări ale abordării SDD în acest proiect:**
- Overhead inițial semnificativ pentru un proiect solo (requirements.md are ~1000 linii)
- Unele cerințe s-au schimbat în timpul implementării (paginare, academic APIs) — necesitând actualizare retroactivă a spec-urilor
- Property-based tests opționale (marcate cu `*`) nu au fost toate implementate din lipsă de timp

### 1.2 Obiective Atinse

Lucrarea de față a prezentat proiectarea și implementarea unui **sistem hibrid de recomandare a surselor academice** pentru lucrări de licență, care îndeplinește următoarele obiective:

- **Retrieval hibrid funcțional** — combinarea căutării semantice (FAISS + sentence-transformers) cu căutarea lexicală (BM25) prin Reciprocal Rank Fusion, oferind rezultate superioare oricărei metode individuale
- **Integrare surse multiple** — corpus local indexat, API-uri academice (Semantic Scholar, arXiv), și căutare web live (DuckDuckGo), toate fuzionate într-un singur răspuns
- **Suport bilingv transparent** — queries în română sau engleză, cu retrieval cross-lingual (o interogare în română găsește articole în engleză și invers)
- **Verificare automată a calității** — detectare clickbait prin compararea similarității titlu vs. conținut, cu avertismente localizate
- **Sistem de feedback** — rating 1-5 stele cu persistență și boost opțional în ranking
- **Interfață web completă** — fără framework, cu dark mode, i18n, paginare, autentificare, și articole salvate
- **Dezvoltare ghidată de specificații** — metodologie Spec-Driven Development cu trasabilitate completă de la cerințe la cod

### 1.2 Contribuții Originale

Sistemul se diferențiază de soluțiile existente (Semantic Scholar, Elicit, Research Rabbit) prin:

1. **Combinația specifică de tehnici** — hybrid retrieval (semantic + BM25 + web) cu content verification și feedback loop, într-un singur sistem integrat
2. **Cross-lingual nativ** — un singur model multilingv servește ambele limbi fără indexuri separate
3. **Self-hosted și transparent** — open-source, rulează local, utilizatorul vede exact de ce un articol a fost recomandat (scor, sursă)
4. **Verificare calitate automată** — niciun produs comercial nu oferă detectare clickbait integrată în pipeline-ul de recomandare

### 1.3 Validare

Sistemul a fost validat prin:
- **23 teste de contract** verificând conformitatea cu specificația OpenAPI
- **12 teste de integrare** end-to-end pe endpoint-uri
- **8 proprietăți de corectitudine** formalizate pentru property-based testing
- **Pipeline CI/CD cu validare spec** — GitHub Actions cu:
  - `validate-openapi`: Validare structurală a `openapi.yaml` cu `openapi-spec-validator`
  - `contract-test`: Teste de contract generate automat din spec cu `schemathesis` (property-based HTTP fuzzing)
  - `test`: pytest + flake8
  - `build-docker`: Build imagine Docker (doar dacă spec-ul e valid + testele trec)
- **Benchmark de performanță** cu măsurători reale pe fiecare componentă (script `benchmark_performance.py`)

### 1.4 Performanță Măsurată

Rezultate din benchmark-ul automatizat (8 queries × 5 iterații, corpus local de 33 articole):

| Componentă | Mean | Median | P95 |
|-----------|------|--------|-----|
| Language Detection | 53ms | 5.5ms | 17ms |
| Embedding Encode (sentence-transformers) | 52ms | 51ms | 68ms |
| FAISS Search (index only) | <0.1ms | <0.1ms | 0.1ms |
| Semantic Retriever (encode + FAISS + metadata) | 48ms | 47ms | 52ms |
| Keyword Retriever (BM25) | 0.4ms | 0.5ms | 0.8ms |
| Hybrid Ranker (RRF fusion) | 0.1ms | 0.1ms | 0.1ms |
| Content Verifier (clickbait detection) | 189ms | 187ms | 223ms |
| **End-to-End (local, fără web)** | **833ms** | **821ms** | **938ms** |

**Observații**:
- Bottleneck-ul principal este Content Verifier (~189ms) care face 2× encode per articol pentru comparare similaritate
- FAISS search e sub-milisecundă chiar și fără GPU — datorită IndexFlatIP optimizat
- BM25 e neglijabil ca latență (~0.5ms)
- Inițializarea modelului embedding durează ~13.5s (one-time, la pornirea serverului)
- Memoria totală: ~420MB (dominat de modelul sentence-transformers)

**Resurse utilizate**:

| Resursă | Dimensiune |
|---------|-----------|
| FAISS Index (33 vectori × 768 dim) | 0.10 MB |
| BM25 Index | 0.02 MB |
| Articles DB (SQLite) | 0.06 MB |
| Embedding Model (paraphrase-multilingual-mpnet-base-v2) | ~420 MB |

---

## 2. Limitări Actuale

| Limitare | Impact | Cauză |
|----------|--------|-------|
| Corpus mic (33 articole) | Rezultate limitate pentru teme diverse | Ingestie manuală, fără automatizare |
| Fără GPU | Encoding query ~50ms (vs ~5ms pe GPU) | Proiect academic, hardware limitat |
| Content Verifier costisitor | ~189ms per request (2× encode per articol) | Reutilizează modelul embedding pentru fiecare item verificat |
| Inițializare lentă | ~13.5s la pornirea serverului | Modelul embedding trebuie încărcat integral în memorie |
| SQLite | Nu scalează la mii de utilizatori concurenți | Alegere simplitate vs. performanță |
| Password hashing simplificat | SHA-256 în loc de bcrypt/argon2 | Prototip academic |
| Fără evaluare formală IR | Nu s-au calculat precision@k, recall@k, nDCG | Lipsă dataset benchmark etichetat |
| Web search rate limiting | DuckDuckGo poate limita la utilizare intensivă | API gratuit fără SLA |
| Latență end-to-end ~833ms (local) | Sub pragul de 1s, dar perceptibilă | Dominat de encoding + content verification |

---

## 3. Direcții Viitoare

### 3.1 Automatizarea Încărcării Resurselor

**Problemă actuală**: Articolele trebuie adăugate manual prin CLI (`python -m app.main ingest`), ceea ce limitează acoperirea sistemului la teme diverse.

**Soluție propusă**: Un pipeline automat de descoperire și ingestie:

```
Scheduler (zilnic/săptămânal)
    │
    ├── Crawl Semantic Scholar → articole noi pe teme populare
    ├── Crawl arXiv → preprint-uri recente din CS/Math
    ├── Crawl DBLP → conferințe și jurnale indexate
    │
    ▼
Evaluare relevanță (embedding similarity cu corpusul existent)
    │
    ▼
Ingestie automată (dacă scor relevanță > prag)
    │
    ▼
Rebuild indexuri (FAISS + BM25)
```

**Beneficii**: Corpus în creștere continuă, acoperire pentru orice temă de licență, fără intervenție manuală.

---

### 3.2 Panou de Administrare (Admin Page)

**Problemă actuală**: Gestionarea corpusului, utilizatorilor, și configurației necesită acces la terminal și editare manuală.

**Soluție propusă**: Interfață web de administrare cu:

| Funcționalitate | Descriere |
|----------------|-----------|
| **Dashboard** | Statistici: nr. articole, nr. utilizatori, nr. căutări, rating-uri |
| **Gestiune corpus** | Upload fișiere (JSON/CSV/BibTeX), ștergere articole, vizualizare metadata |
| **Gestiune utilizatori** | Listare, dezactivare conturi, reset parole |
| **Configurare live** | Editare `config.yaml` din browser (weights, thresholds, provider) |
| **Logs** | Vizualizare erori, queries populare, retriever failures |
| **Domain blocklist** | Adăugare/ștergere domenii blocate din UI |

**Implementare**: Blueprint Flask separat (`/admin/`) cu autentificare role-based (admin vs. user).

---

### 3.3 Integrare LLM — Chatbot de Cercetare

**Problemă actuală**: Utilizatorul primește o listă de articole dar nu are asistență în interpretarea sau utilizarea lor.

**Soluție propusă**: Un chatbot conversațional (bazat pe Ollama/LLM local) care:

| Capabilitate | Exemplu interacțiune |
|-------------|---------------------|
| **Query enhancement** | "Reformulează titlul meu pentru căutare mai bună" |
| **Explicare relevanță** | "De ce e relevant acest articol pentru teza mea?" |
| **Sumarizare** | "Rezumă abstractul acestui articol în 2 propoziții" |
| **Comparare** | "Compară aceste 3 articole — care e mai relevant?" |
| **Sugestii structură** | "Ce capitole ar trebui să aibă teza mea pe baza surselor găsite?" |
| **Generare bibliografie** | "Generează secțiunea de referințe pentru articolele salvate" |

**Arhitectură**:
```
User ←→ Chat UI ←→ LLM Agent (Ollama) ←→ Retrieval Pipeline
                                        ←→ Saved Articles Context
```

**Model recomandat**: Llama 3.2 (3B) sau Mistral (7B) — gratuit, local, fără API key.

---

### 3.4 Directoare de Proiecte (Multi-Project Support)

**Problemă actuală**: Un utilizator poate lucra la o singură teză. Dacă are mai multe proiecte de cercetare, trebuie să gestioneze manual ce articole aparțin cărui proiect.

**Soluție propusă**:

```
User Account
├── Proiect 1: "Licență — Sisteme de recomandare"
│   ├── Articole salvate (15)
│   ├── Istoric căutări
│   ├── Rating-uri specifice proiectului
│   └── Note personale
├── Proiect 2: "Disertație — NLP aplicat"
│   ├── Articole salvate (8)
│   └── ...
└── Proiect 3: "Paper conferință"
    └── ...
```

**Funcționalități**:
- Creare/ștergere proiecte
- Salvare articole per proiect (nu global)
- Feedback signal boost per proiect (articolele bune pentru un proiect nu influențează altul)
- Export proiect (bibliografie, note, articole salvate)

---

### 3.5 Swagger UI Integrat pentru Dezvoltatori

**Problemă actuală**: Documentația API există în `docs/` dar necesită generare manuală și servire separată.

**Soluție propusă**: Swagger UI servit direct de Flask la `/api/docs`:

```python
@app.route("/api/docs")
def swagger_ui():
    return render_template("swagger-ui.html", spec_url="/api/openapi.yaml")

@app.route("/api/openapi.yaml")
def openapi_spec():
    return send_file("openapi.yaml", mimetype="text/yaml")
```

**Beneficii**:
- Documentație mereu actualizată (servită din același server)
- "Try it out" direct din browser
- Util pentru dezvoltatori care vor să integreze API-ul
- Referință rapidă pentru frontend developers

---

### 3.6 Generare Citări LaTeX

**Problemă actuală**: Utilizatorul găsește articole relevante dar trebuie să formateze manual citările pentru lucrare.

**Soluție propusă**: Buton "Copiază citare" pe fiecare card de articol, cu formate multiple:

| Format | Exemplu output |
|--------|---------------|
| **BibTeX** | `@article{vaswani2017attention, title={Attention Is All You Need}, author={Vaswani, A. and ...}, year={2017}, doi={10.48550/...}}` |
| **APA** | Vaswani, A., Shazeer, N., ... (2017). Attention Is All You Need. *arXiv preprint*. |
| **IEEE** | [1] A. Vaswani et al., "Attention Is All You Need," 2017, doi: 10.48550/... |
| **Harvard** | Vaswani, A. et al. (2017) 'Attention Is All You Need', *arXiv*. |

**Implementare**:
```python
def generate_bibtex(article: Article) -> str:
    """Generează citare BibTeX din metadata articolului."""
    key = article.doi.replace("/", "_") if article.doi else article.id[:12]
    authors = " and ".join(article.authors)
    return f"""@article{{{key},
  title={{{article.title}}},
  author={{{authors}}},
  year={{{article.year}}},
  doi={{{article.doi or ""}}}
}}"""
```

**UI**: Dropdown pe card → selectare format → copiere în clipboard cu un click.

**Export bulk**: Buton "Exportă toate salvate ca BibTeX" → descarcă fișier `.bib` cu toate articolele salvate.

---

## 4. Reflecție asupra Metodologiei SDD

### 4.1 Cum ar fi Implementate Funcționalitățile Viitoare cu SDD

Fiecare funcționalitate din secțiunea 3 ar urma același flux:

```
1. requirements.md — Definire user stories + acceptance criteria
2. design.md — Algoritmi, API contracts, diagrame
3. tasks.md — Breakdown în sub-task-uri cu referințe la cerințe
4. Implementare — Cod conform design-ului
5. Validare — Teste unitare + property-based + integration
```

**Exemplu: Automatizare Ingestie**

```markdown
# requirements.md (extras)
### Requirement 13: Automated Corpus Expansion

**User Story:** As an operator, I want the system to automatically discover 
and ingest new articles from academic APIs, so that the corpus grows without 
manual intervention.

#### Acceptance Criteria
1. THE System SHALL query Semantic Scholar API daily for new articles 
   matching configurable topic keywords.
2. THE System SHALL evaluate each discovered article's relevance to the 
   existing corpus using embedding similarity.
3. IF the relevance score exceeds a configurable threshold (default 0.7), 
   THEN THE System SHALL automatically ingest the article.
4. THE System SHALL log all ingestion decisions (accepted/rejected) with 
   relevance scores for auditability.
```

### 4.2 Evoluția Specificațiilor

Pe măsură ce sistemul crește, specificațiile evoluează:

| Versiune | Cerințe | Componente Design | Task-uri |
|----------|:-------:|:-----------------:|:--------:|
| v1.0 (actual) | 12 | 10 | 19 |
| v2.0 (propus) | 18 (+6 noi) | 14 (+4 noi) | ~30 |

Noile cerințe (13-18) ar acoperi: automatizare ingestie, admin page, LLM chatbot, multi-project, Swagger integrat, citări LaTeX.

### 4.3 Rolul Kiro în Dezvoltarea Viitoare

Mediul Kiro facilitează extinderea prin:
- **Steering files** actualizate cu noile componente
- **Skills** pentru workflow-uri specifice (ex: `#ollama-agent` pentru integrare LLM)
- **Specs** noi pentru fiecare feature major
- **MCP servers** adăugați pentru acces la API-uri noi (Semantic Scholar, admin DB)
- **Hooks** pentru automatizare (ex: rebuild indexes post-ingestie)

---

## 5. Prioritizare Dezvoltări

| # | Funcționalitate | Impact | Efort | Prioritate |
|---|----------------|--------|-------|:----------:|
| 1 | Automatizare ingestie | Mare (acoperire corpus) | Mediu | 🔴 Înaltă |
| 2 | Citări LaTeX | Mare (utilitate directă) | Mic | 🔴 Înaltă |
| 3 | LLM chatbot | Mare (diferențiere piață) | Mare | 🟡 Medie |
| 4 | Directoare proiecte | Mediu (organizare) | Mediu | 🟡 Medie |
| 5 | Admin page | Mediu (operare) | Mediu | 🟡 Medie |
| 6 | Swagger UI integrat | Mic (DX) | Mic | 🟢 Scăzută |

---

## 6. Viziune pe Termen Lung

Sistemul Hybrid Thesis Recommender poate evolua de la un instrument de căutare într-un **asistent complet de cercetare**:

```
Azi (v1.0)                    Viitor (v2.0+)
─────────────                 ──────────────────────────────
Căutare articole              Asistent conversațional AI
Lista de rezultate            Sumarizare + explicare relevanță
Rating manual                 Învățare din comportament
Un singur proiect             Multi-proiect cu organizare
Corpus static                 Corpus auto-actualizat zilnic
Citare manuală                Export BibTeX/APA automat
Fără admin                    Dashboard complet de administrare
```

Această evoluție transformă produsul dintr-un **motor de căutare specializat** într-o **platformă de asistență academică** — un companion de cercetare care înțelege contextul tezei, învață din preferințele utilizatorului, și automatizează sarcinile repetitive ale procesului de documentare.
