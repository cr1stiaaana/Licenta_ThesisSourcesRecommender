# Containerizare cu Docker

## 1. Motivație — De ce Docker?

### 1.1 Problema „funcționează pe mașina mea"

Aplicația Hybrid Thesis Recommender depinde de un ecosistem complex de biblioteci: sentence-transformers (care la rândul lui necesită PyTorch), FAISS cu dependențe C++ compilate (libgomp pentru OpenMP), rank_bm25, Flask, și multiple biblioteci auxiliare. Instalarea manuală pe o mașină nouă implică:

- Instalarea versiunii corecte de Python (3.10+)
- Compilarea dependențelor native (FAISS necesită instrucțiuni SIMD specifice procesorului)
- Configurarea corectă a căilor de sistem (PATH, LD_LIBRARY_PATH)
- Rezolvarea conflictelor între versiuni de pachete

Pe mașina dezvoltatorului, toate acestea funcționează deoarece au fost configurate incremental pe parcursul lunilor de dezvoltare. Dar pe o mașină nouă (a unui coleg, a unui evaluator, sau a unui server de producție), reproducerea exactă a mediului este fragilă și consumatoare de timp.

### 1.2 Ce oferă Docker

Docker rezolvă această problemă prin **containerizare** — împachetarea aplicației împreună cu toate dependențele sale într-o imagine autonomă care rulează identic pe orice mașină cu Docker instalat. Containerul include:

- Sistemul de operare de bază (Python 3.10-slim, bazat pe Debian)
- Toate bibliotecile Python instalate la versiunile exacte din `requirements.txt`
- Dependențele native compilate (libgomp1 pentru FAISS)
- Codul aplicației și configurația
- Structura de directoare necesară la runtime

### 1.3 Beneficii concrete pentru proiect

| Beneficiu | Fără Docker | Cu Docker |
|-----------|------------|-----------|
| **Setup pe mașină nouă** | 30-60 minute (instalare Python, pip install, rezolvare erori compilare FAISS) | 1 comandă: `docker pull` + `docker run` |
| **Reproducibilitate** | „La mine merge" — versiuni diferite pe mașini diferite | Identic peste tot — aceeași imagine, același comportament |
| **Izolare** | Conflicte cu alte aplicații Python de pe sistem | Container izolat, nu afectează și nu e afectat de restul sistemului |
| **Deploy în producție** | Configurare manuală server, instalare dependențe | Push imagine pe registry → pull pe server → run |
| **CI/CD** | Testele depind de mediul runner-ului | Build imaginea → testează în container → publică |
| **Scalare** | O singură instanță | Multiple containere din aceeași imagine (orchestrare cu Docker Compose sau Kubernetes) |

---

## 2. Arhitectura Dockerfile-ului

### 2.1 Multi-Stage Build

Proiectul folosește un Dockerfile cu două etape (multi-stage build), o practică standard pentru reducerea dimensiunii imaginii finale:

```dockerfile
# Etapa 1: Builder — compilare dependențe
FROM python:3.10-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa 2: Runtime — doar ce e necesar la execuție
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
```

**De ce două etape:**

Etapa de build necesită `build-essential` (compilatoare C/C++, make) pentru a instala pachete cu extensii native (FAISS, numpy). Aceste unelte ocupă ~200MB și nu sunt necesare la runtime. Prin copierea doar a pachetelor instalate (`/root/.local`) în imaginea finală, se elimină compilatoarele, reducând dimensiunea imaginii cu ~200MB.

### 2.2 Structura imaginii finale

```dockerfile
# Copiază codul aplicației
COPY app/ ./app/
COPY static/ ./static/
COPY config.yaml .
COPY database/ ./database/

# Creează directorul pentru date runtime
RUN mkdir -p data

# Expune portul
EXPOSE 5000

# Variabile de mediu
ENV FLASK_APP=app.main
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_OFFLINE=0
```

**Ce intră în imagine:**
- `app/` — codul Python al aplicației
- `static/` — fișierele frontend (HTML, CSS, JS)
- `config.yaml` — configurația implicită
- `database/` — schema SQL

**Ce NU intră în imagine** (definit în `.dockerignore`):
- `data/` (baze de date, indexuri) — montate ca volum la runtime
- `tests/` — nu sunt necesare în producție
- `.git/`, `.kiro/`, `theory_files/` — doar dezvoltare
- `venv/`, `__pycache__/` — artefacte locale

### 2.3 Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)"
```

Health check-ul verifică periodic că serverul răspunde. Parametrii:
- `start-period=60s` — acordă 60 de secunde la pornire pentru încărcarea modelului embedding (~14s) plus o marjă de siguranță
- `interval=30s` — verifică la fiecare 30 de secunde
- `retries=3` — declară containerul „unhealthy" doar după 3 eșecuri consecutive
- `timeout=10s` — dacă serverul nu răspunde în 10s la o verificare, o consideră eșuată

Acest mecanism permite orchestratorilor (Docker Compose, Kubernetes) să detecteze automat când containerul nu mai funcționează și să-l repornească.

---

## 3. Cum ajută Docker proiectul

### 3.1 Portabilitate

Imaginea Docker funcționează identic pe:
- Windows (prin Docker Desktop)
- macOS (prin Docker Desktop)
- Linux (Docker nativ)
- Servere cloud (AWS, GCP, Azure)
- CI/CD (GitHub Actions — exact ce se întâmplă în pipeline-ul nostru)

Dezvoltatorul lucrează pe Windows, CI-ul rulează pe Ubuntu, iar un server de producție poate fi orice distribuție Linux. Docker elimină diferențele între aceste medii.

### 3.2 Separarea codului de date

Prin convenția definită în `.dockerignore` și structura containerului, se realizează o separare clară:

```
Imagine Docker (read-only, versionată)     Volume (read-write, persistent)
├── app/ (cod)                             ├── data/articles.db
├── static/ (frontend)                     ├── data/faiss.index
├── config.yaml (default)                  ├── data/bm25.pkl
└── requirements instalate                 ├── data/feedback.db
                                           └── data/users.db
```

Imaginea conține codul (care se schimbă la fiecare release), iar datele (care persistă între deploy-uri) sunt montate ca volum extern. Acest model permite:
- Actualizarea aplicației fără pierderea datelor
- Backup independent al datelor
- Utilizarea acelorași date cu versiuni diferite ale aplicației (rollback)

### 3.3 Integrare cu CI/CD

În pipeline-ul GitHub Actions, Docker joacă două roluri:

1. **Validare** (job `build-docker` din CI) — verifică că aplicația se poate containeriza cu succes; dacă Dockerfile-ul are erori sau o dependență lipsește, build-ul eșuează
2. **Publicare** (workflow `docker-publish.yml`) — la crearea unui tag de versiune, imaginea e construită și publicată pe GitHub Container Registry, gata de deploy

### 3.4 Simplificarea deploy-ului

Fără Docker, deploy-ul pe un server nou necesită:
1. Instalare Python 3.10
2. Instalare pip și virtualenv
3. Clone repository
4. pip install requirements (poate eșua la compilare FAISS)
5. Configurare variabile de mediu
6. Pornire server cu parametrii corecți

Cu Docker:
```bash
docker pull ghcr.io/{owner}/article-recommender:1.0.0
docker run -d -p 5000:5000 -v ./data:/app/data ghcr.io/{owner}/article-recommender:1.0.0
```

Două comenzi, indiferent de sistemul de operare al serverului.

---

## 4. Comenzi de utilizare

### 4.1 Build local

```bash
# Construiește imaginea din Dockerfile
docker build -t thesis-recommender:latest .

# Verifică dimensiunea
docker images thesis-recommender
```

### 4.2 Rulare container

```bash
# Pornire cu volum pentru date persistente
docker run -d \
  --name recommender \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  thesis-recommender:latest

# Verificare logs
docker logs recommender

# Oprire
docker stop recommender
```

### 4.3 Utilizare din registry

```bash
# Descărcare imagine publicată
docker pull ghcr.io/{owner}/article-recommender:1.0.0

# Rulare
docker run -d -p 5000:5000 -v ./data:/app/data \
  ghcr.io/{owner}/article-recommender:1.0.0
```

---

## 5. Limitări și considerații

| Aspect | Detaliu |
|--------|---------|
| **Dimensiune imagine** | ~1.5-2GB (dominat de PyTorch + sentence-transformers); se poate reduce cu model mai mic |
| **Cold start container** | ~14s (încărcare model embedding la pornire) |
| **Model embedding** | Nu e inclus în imagine (se descarcă la prima rulare); alternativ se poate include la build pentru deploy offline |
| **Fără GPU** | Imaginea actuală e CPU-only; pentru GPU e nevoie de `nvidia/cuda` ca bază și `faiss-gpu` |
| **Date externe** | Volumul cu datele trebuie gestionat separat (backup, migrare) |
| **Single container** | Nu include orchestrare (pentru scalare ar fi nevoie de Docker Compose sau Kubernetes) |

---

## 6. Evoluții posibile

- **Include modelul în imagine** — adaugă un step de download la build (`RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"`) pentru deploy offline, eliminând cold start-ul de download
- **Docker Compose** — definire servicii multiple (app + reverse proxy Nginx + monitoring) într-un singur fișier
- **GPU support** — imagine bazată pe `nvidia/cuda` pentru encoding de 10× mai rapid
- **Imagine mai mică** — utilizare model MiniLM (80MB vs 420MB) sau ONNX Runtime pentru a reduce dimensiunea totală
