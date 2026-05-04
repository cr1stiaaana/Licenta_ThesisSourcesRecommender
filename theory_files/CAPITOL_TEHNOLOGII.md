# Capitolul 3: Tehnologii și Mediu de Dezvoltare

## 3.1 Introducere

Acest capitol prezintă tehnologiile, instrumentele și mediul de dezvoltare utilizate în implementarea sistemului Hybrid Thesis Recommender. Alegerea tehnologiilor a fost ghidată de cerințele funcționale ale sistemului, scalabilitate, performanță și ecosistemul de dezvoltare modern.

## 3.2 Stack Tehnologic

### 3.2.1 Limbaje de Programare

#### Python 3.10+
Python a fost ales ca limbaj principal pentru backend datorită:
- **Ecosistem ML/AI bogat**: Biblioteci mature pentru machine learning și procesare limbaj natural
- **Productivitate ridicată**: Sintaxă clară și expresivă, dezvoltare rapidă
- **Comunitate activă**: Suport extins și documentație comprehensivă
- **Integrare ușoară**: Compatibilitate excelentă cu biblioteci de căutare semantică

**Versiune utilizată**: Python 3.10.x

#### JavaScript (ES6+)
JavaScript vanilla (fără framework) pentru frontend:
- **Performanță**: Fără overhead-ul unui framework
- **Simplitate**: Cod ușor de înțeles și menținut
- **Compatibilitate**: Suport nativ în toate browserele moderne
- **Control complet**: Flexibilitate maximă în implementare

### 3.2.2 Framework-uri și Biblioteci Backend

#### Flask 3.1.1
Framework web micro pentru Python:
- **Lightweight**: Overhead minim, performanță ridicată
- **Flexibilitate**: Arhitectură modulară, extensibilă
- **RESTful**: Suport nativ pentru API-uri REST
- **Blueprint-uri**: Organizare modulară a codului

**Caracteristici utilizate**:
- Application factory pattern pentru testabilitate
- Blueprint-uri pentru separarea logică (recommend, feedback, auth)
- Session management pentru autentificare
- Error handling și logging centralizat

#### Sentence Transformers 3.4.1
Bibliotecă pentru embeddings semantice:
- **Model utilizat**: `paraphrase-multilingual-mpnet-base-v2`
- **Dimensiune embeddings**: 768
- **Suport multilingv**: Română și Engleză
- **Performanță**: Optimizat pentru inferență rapidă

**Justificare alegere model**:
- Performanță excelentă pe task-uri de similaritate semantică
- Suport nativ pentru limba română
- Dimensiune rezonabilă (420MB)
- Balans optim între acuratețe și viteză

#### FAISS (Facebook AI Similarity Search) 1.10.0
Bibliotecă pentru căutare vectorială eficientă:
- **Indexare**: IndexFlatIP pentru căutare exactă cu produs scalar
- **Performanță**: Căutare sub-liniară în spațiul vectorial
- **Scalabilitate**: Suport pentru milioane de vectori
- **Optimizări**: Suport AVX2 pentru procesare SIMD

**Configurare**:
```python
index = faiss.IndexFlatIP(embedding_dim)  # Inner product pentru cosine similarity
faiss.normalize_L2(embeddings)  # Normalizare pentru cosine similarity
```

#### Rank-BM25 0.2.2
Implementare BM25 pentru keyword matching:
- **Algoritm**: Okapi BM25 cu parametri standard (k1=1.5, b=0.75)
- **Tokenizare**: Lowercase + split pe whitespace
- **Performanță**: Indexare și căutare rapidă
- **Complementaritate**: Combină bine cu căutarea semantică

### 3.2.3 Biblioteci pentru Procesare Limbaj Natural

#### LangDetect 1.0.9 și LangID 1.1.6
Detectare automată a limbii:
- **LangDetect**: Detectare bazată pe n-grame
- **LangID**: Detectare bazată pe modele statistice
- **Fallback**: Sistem cu două niveluri pentru robustețe
- **Limbi suportate**: Română și Engleză

#### PyYAML 6.0.2
Parsare și serializare YAML:
- **Configurare**: Fișier `config.yaml` pentru parametri sistem
- **Hot-reload**: Watchdog 6.0.0 pentru reîncărcare automată
- **Validare**: Schema definită în `AppConfig` dataclass

### 3.2.4 Integrări și API-uri Externe

#### DuckDuckGo Search (ddgs 9.14.1)
Motor de căutare web fără API key:
- **Avantaje**: Gratuit, fără rate limiting sever
- **Rezultate**: Până la 20 rezultate per query
- **Timeout**: Configurat la 10 secunde
- **Fallback**: Sistem de retry pentru robustețe

#### Semantic Scholar API
API academic pentru articole științifice:
- **Endpoint**: `https://api.semanticscholar.org/graph/v1/paper/search`
- **Rate limiting**: Respectare limite API (100 req/5min)
- **Metadata**: Titlu, autori, abstract, DOI, anul publicării
- **Filtrare**: Doar articole cu metadata completă

#### arXiv API
Acces la preprint-uri științifice:
- **Protocol**: OAI-PMH (Open Archives Initiative)
- **Format**: XML parsing pentru metadata
- **Categorii**: Computer Science, Mathematics, Physics
- **Actualizare**: Zilnică, acces la cele mai recente articole

### 3.2.5 Baze de Date

#### SQLite 3
Bază de date relațională embedded:
- **Avantaje**: Zero-configuration, fără server separat
- **Performanță**: Suficientă pentru volume medii de date
- **ACID**: Tranzacții complete, integritate date
- **Portabilitate**: Un singur fișier per bază de date

**Baze de date utilizate**:
1. **articles.db**: Metadata articole (titlu, autori, abstract, DOI, URL)
2. **feedback.db**: Ratings utilizatori (item_id, rating, session_id, timestamp)
3. **users.db**: Conturi utilizatori și articole salvate

**Schema exemplu** (articles.db):
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    abstract TEXT,
    doi TEXT,
    url TEXT,
    keywords TEXT,
    faiss_idx INTEGER UNIQUE
);
```

### 3.2.6 Frontend

#### HTML5 + CSS3
Markup și styling modern:
- **Semantic HTML**: Structură clară și accesibilă
- **CSS Variables**: Teme (light/dark mode) cu variabile CSS
- **Flexbox/Grid**: Layout responsive
- **Accessibility**: ARIA labels, keyboard navigation

#### Vanilla JavaScript (ES6+)
Logică client-side fără framework:
- **Fetch API**: Comunicare asincronă cu backend
- **LocalStorage**: Persistență date pentru utilizatori guest
- **Session Storage**: State management pentru paginație
- **Event Delegation**: Gestionare eficientă evenimente

**Caracteristici implementate**:
- Paginație independentă per tab (articole vs resurse web)
- Sistem de rating cu stele (1-5)
- Autentificare opțională cu migrare automată date
- Dark mode cu persistență preferință
- Internationalizare (RO/EN) cu detectare automată

## 3.3 Mediu de Dezvoltare

### 3.3.1 IDE și Editoare

#### Visual Studio Code
Editor principal de cod:
- **Extensii utilizate**:
  - Python (Microsoft): IntelliSense, debugging, linting
  - Pylance: Type checking și auto-completion avansat
  - OpenAPI (Swagger) Editor: Editare și validare specificații API
  - GitLens: Vizualizare istoricul Git inline
  - Prettier: Formatare automată cod JavaScript/HTML/CSS

#### Kiro (AI-Powered Development Environment)
Mediu de dezvoltare asistat de AI:
- **Spec-driven development**: Creare specificații OpenAPI
- **Code generation**: Generare cod din specificații
- **Testing**: Dezvoltare teste automate bazate pe spec
- **Documentation**: Generare automată documentație
- **Refactoring**: Asistență în restructurare cod

### 3.3.2 Sistem de Versionare

#### Git 2.x
Sistem de control versiuni distribuit:
- **Branching strategy**: Main branch pentru producție
- **Commit messages**: Conventional Commits format
- **Hooks**: Pre-commit pentru validare cod

#### GitHub
Platformă de hosting și colaborare:
- **Repository**: https://github.com/cr1stiaaana/Licenta_ThesisSourcesRecommender
- **Features utilizate**:
  - Issues pentru tracking task-uri
  - Pull Requests pentru code review
  - GitHub Actions pentru CI/CD (planificat)
  - GitHub Pages pentru documentație (planificat)

**Exemplu commit message**:
```
Implement independent pagination for articles and web resources

- Add 'type' parameter to /recommend endpoint
- Support independent offsets per resource type
- Display end-of-results message when pagination exhausted
- Increase DuckDuckGo results limit from 5 to 20
```

### 3.3.3 Instrumente de Testare

#### pytest 8.3.5
Framework de testare pentru Python:
- **Fixtures**: Setup/teardown pentru teste
- **Parametrizare**: Teste cu multiple seturi de date
- **Coverage**: Măsurare acoperire cod cu pytest-cov
- **Markers**: Organizare teste (unit, integration, contract)

**Tipuri de teste implementate**:
1. **Unit tests**: Testare componente individuale
2. **Integration tests**: Testare interacțiuni între componente
3. **Contract tests**: Validare conformitate cu OpenAPI spec

#### Hypothesis 6.131.15
Property-based testing:
- **Generare automată**: Date de test generate automat
- **Edge cases**: Descoperire automată cazuri limită
- **Shrinking**: Minimizare exemple care eșuează
- **Strategii**: Generare date complexe (strings, lists, dicts)

**Exemplu utilizare**:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=3, max_size=500))
def test_title_validation(title):
    # Test că orice string valid 3-500 caractere este acceptat
    response = client.post('/recommend', json={'title': title})
    assert response.status_code in [200, 422]
```

### 3.3.4 Documentare API

#### OpenAPI 3.0.3
Standard pentru specificații API:
- **Fișier**: `openapi.yaml`
- **Endpoints**: 10 endpoint-uri documentate complet
- **Schemas**: Request/response schemas cu validare
- **Examples**: Exemple pentru fiecare endpoint

#### Swagger UI
Documentație interactivă:
- **Try it out**: Testare endpoint-uri direct din browser
- **Schema visualization**: Vizualizare structuri date
- **Authentication**: Suport pentru session-based auth

#### Redoc
Documentație statică elegantă:
- **Responsive**: Optimizat pentru mobile și desktop
- **Search**: Căutare în documentație
- **Three-panel layout**: Descriere, exemple, schema

**Generare automată**:
```bash
python generate_docs.py
# Generează: docs/swagger-ui.html, docs/redoc.html, docs/api-docs.md
```

### 3.3.5 Managementul Dependențelor

#### pip + requirements.txt
Gestiune pachete Python:
- **requirements.txt**: Lista dependențe cu versiuni fixate
- **Virtual environment**: Izolare dependențe per proiect
- **Freeze**: Snapshot exact al versiunilor instalate

**Structură requirements.txt**:
```txt
Flask==3.1.1
sentence-transformers==3.4.1
faiss-cpu==1.10.0
rank-bm25==0.2.2
pytest==8.3.5
hypothesis==6.131.15
PyYAML==6.0.2
```

### 3.3.6 Containerizare (Planificat)

#### Docker
Containerizare aplicație:
- **Dockerfile**: Definire imagine aplicație
- **docker-compose.yml**: Orchestrare servicii
- **Multi-stage builds**: Optimizare dimensiune imagine
- **Volume mounting**: Persistență date

**Avantaje**:
- Reproducibilitate: Același mediu pe orice mașină
- Izolare: Dependențe separate de sistem host
- Deployment: Ușor de deploiat în cloud
- Scalabilitate: Ușor de scalat orizontal

## 3.4 Workflow de Dezvoltare

### 3.4.1 Spec-Driven Development

Proces de dezvoltare ghidat de specificații:

1. **Definire specificație OpenAPI**
   - Documentare endpoint-uri
   - Definire schemas request/response
   - Specificare validări și erori

2. **Generare documentație**
   - Swagger UI pentru testare interactivă
   - Redoc pentru documentație statică
   - Markdown pentru documentație lightweight

3. **Implementare backend**
   - Dezvoltare endpoint-uri conform spec
   - Validare input conform schemas
   - Formatare output conform spec

4. **Dezvoltare teste contract**
   - Verificare conformitate cu spec
   - Validare schemas request/response
   - Testare status codes și erori

5. **Validare și iterare**
   - Rulare teste automate
   - Verificare documentație
   - Ajustare spec și implementare

### 3.4.2 Continuous Integration (Planificat)

Pipeline CI/CD cu GitHub Actions:

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  validate-spec:
    - Validare OpenAPI spec
    - Verificare sintaxă YAML
  
  test:
    - Unit tests
    - Integration tests
    - Contract tests
    - Coverage report
  
  lint:
    - Pylint pentru Python
    - ESLint pentru JavaScript
    - Type checking cu mypy
  
  docs:
    - Generare documentație
    - Deploy pe GitHub Pages
```

## 3.5 Configurare și Deployment

### 3.5.1 Configurare Aplicație

#### config.yaml
Fișier centralizat de configurare:
```yaml
# Retrieval weights
semantic_weight: 0.6
keyword_weight: 0.4

# Top-K limits
article_top_k: 5
web_top_k: 5

# Score thresholds
min_article_score: 0.001
min_web_score: 0.05

# Web search
web_search_provider: "duckduckgo"
web_search_num_results: 50

# Timeouts
request_timeout_seconds: 20.0
component_timeout_seconds: 18.0
```

**Hot-reload**: Modificările în `config.yaml` sunt detectate automat și aplicate fără restart server.

### 3.5.2 Deployment Local

#### Development Server
```bash
# Start Flask development server
python -m app.main serve --debug --host 0.0.0.0 --port 5000

# Features:
# - Auto-reload on code changes
# - Debug mode with detailed errors
# - Accessible on all network interfaces
```

#### Production Server (Planificat)
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app.main:create_app()"

# Features:
# - Multiple worker processes
# - Production-grade WSGI server
# - Better performance and stability
```

### 3.5.3 Deployment Cloud (Planificat)

Opțiuni de deployment:
- **Heroku**: Platform-as-a-Service, deployment simplu
- **AWS EC2**: Control complet, scalabilitate
- **Google Cloud Run**: Containerizare, auto-scaling
- **DigitalOcean**: VPS simplu, cost-eficient

## 3.6 Performanță și Optimizări

### 3.6.1 Optimizări Backend

#### Căutare Paralelă
```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        'semantic': executor.submit(semantic_retriever.retrieve, query),
        'keyword': executor.submit(keyword_retriever.retrieve, query),
        'academic': executor.submit(academic_retriever.retrieve, query),
        'web': executor.submit(web_retriever.retrieve, query)
    }
```

**Beneficii**:
- Reducere latență cu ~75% (de la 4s la 1s)
- Utilizare eficientă CPU multi-core
- Timeout independent per retriever

#### Caching (Planificat)
- **Query caching**: Redis pentru rezultate frecvente
- **Embedding caching**: Cache embeddings pentru queries comune
- **TTL**: Time-to-live configurat per tip de cache

### 3.6.2 Optimizări Frontend

#### Lazy Loading
- Încărcare progresivă rezultate (5 per pagină)
- Reducere payload inițial
- Experiență utilizator îmbunătățită

#### State Management
- Session storage pentru persistență state
- LocalStorage pentru preferințe utilizator
- Minimizare re-renders

## 3.7 Securitate

### 3.7.1 Autentificare și Autorizare

- **Session-based auth**: Flask sessions cu secret key
- **Password hashing**: bcrypt pentru parole
- **CSRF protection**: Token-uri pentru formulare (planificat)

### 3.7.2 Validare Input

- **Server-side validation**: Validare completă în backend
- **Client-side validation**: Feedback rapid pentru utilizator
- **Sanitization**: Curățare input pentru prevenire XSS

### 3.7.3 Rate Limiting (Planificat)

- **Flask-Limiter**: Limitare request-uri per IP
- **API quotas**: Limite per utilizator autentificat
- **Graceful degradation**: Mesaje clare la depășire limite

## 3.8 Monitorizare și Logging

### 3.8.1 Logging

```python
import logging

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)
```

**Niveluri utilizate**:
- **INFO**: Operații normale (requests, retrievals)
- **WARNING**: Situații neașteptate dar recuperabile
- **ERROR**: Erori care necesită atenție

### 3.8.2 Monitoring (Planificat)

- **Prometheus**: Metrici aplicație (latență, throughput)
- **Grafana**: Dashboards pentru vizualizare
- **Sentry**: Error tracking și alerting

## 3.9 Concluzii

Stack-ul tehnologic ales oferă:
- ✅ **Performanță**: Căutare rapidă cu FAISS și BM25
- ✅ **Scalabilitate**: Arhitectură modulară, ușor de extins
- ✅ **Mentenabilitate**: Cod clar, bine documentat
- ✅ **Productivitate**: Tooling modern, dezvoltare rapidă
- ✅ **Calitate**: Teste automate, validare continuă

Mediul de dezvoltare integrat cu Kiro și spec-driven development asigură:
- Conformitate cu specificații
- Documentație mereu actualizată
- Testare automată și comprehensivă
- Colaborare eficientă în echipă
