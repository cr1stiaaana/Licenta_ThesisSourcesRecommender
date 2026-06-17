---
name: deployment
description: Ghid deploy local, Docker și cloud pentru Hybrid Thesis Recommender.
version: 1.0.0
---

# Skill: Deployment

## Overview

This skill guides deploying the Hybrid Thesis Recommender — locally, with Docker, or to cloud.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# First run (downloads embedding model ~420MB)
python app/main.py serve --debug --port 5000

# With custom host (accessible on network)
python app/main.py serve --host 0.0.0.0 --port 8080
```

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t thesis-recommender .

# Run container
docker run -p 5000:5000 -v ./data:/app/data thesis-recommender

# With docker-compose
docker-compose up -d
```

### Docker Compose Services

```yaml
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data        # Persist databases and indexes
      - ./config.yaml:/app/config.yaml  # External config
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### Multi-stage Dockerfile Tips

- Stage 1: Install dependencies (cached layer)
- Stage 2: Copy app code (changes frequently)
- Use `.dockerignore` to exclude `data/`, `.git/`, `node_modules/`
- Pin base image: `python:3.10-slim`

## Production Considerations

### WSGI Server

Don't use Flask dev server in production:
```bash
# Gunicorn (Linux/Mac)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app.api:create_app()"

# Waitress (Windows-compatible)
pip install waitress
waitress-serve --port=5000 app.api:create_app
```

### Environment Variables

```bash
# Required for production
FLASK_SECRET_KEY=<random-32-char-string>
FLASK_ENV=production

# Optional
WEB_SEARCH_API_KEY=<if using Google CSE or Bing>
OLLAMA_BASE_URL=http://localhost:11434
```

### Data Persistence

Files that must persist across deployments:
- `data/articles.db` — article metadata
- `data/faiss.index` — vector embeddings
- `data/bm25.pkl` — BM25 index
- `data/feedback.db` — user ratings
- `data/users.db` — user accounts

### Health Check

```bash
# Simple health check endpoint
curl http://localhost:5000/health

# Verify recommendations work
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{"title": "machine learning in healthcare"}'
```

## Cloud Deployment Options

| Platform | Difficulty | Cost | Notes |
|----------|:----------:|------|-------|
| Railway | Easy | Free tier | Git push to deploy |
| Render | Easy | Free tier | Auto-deploy from GitHub |
| DigitalOcean App | Medium | $5/mo | Docker-based |
| AWS EC2 | Hard | $5-20/mo | Full control |
| Google Cloud Run | Medium | Pay-per-use | Serverless containers |

## Pre-Deployment Checklist

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] `config.yaml` has production values (debug=false)
- [ ] Secret key is set and not committed to git
- [ ] Data files are backed up
- [ ] Docker image builds successfully
- [ ] Health check responds after deploy
- [ ] Web search works (API keys configured if needed)
