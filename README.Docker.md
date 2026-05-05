# Docker Deployment Guide - Hybrid Thesis Recommender

## 🐳 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Build and Run

```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at: **http://localhost:5000**

---

## 📦 What's Included

### Multi-Stage Build

The Dockerfile uses a multi-stage build to:
1. **Builder stage**: Install dependencies and download the embedding model
2. **Final stage**: Copy only runtime files (smaller image)

### Features

- ✅ **Optimized image size**: Multi-stage build reduces final image size
- ✅ **Cached model**: Embedding model downloaded during build (not at runtime)
- ✅ **Health checks**: Automatic container health monitoring
- ✅ **Volume mounts**: Data persistence and config hot-reload
- ✅ **Production-ready**: Proper logging, restart policies

---

## 🔧 Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
```

### Volumes

The following directories are mounted:

```yaml
volumes:
  - ./data:/app/data              # Persistent data (databases, indexes)
  - ./config.yaml:/app/config.yaml:ro  # Config file (read-only)
```

### Ports

Default port mapping: `5000:5000`

To change the host port:

```yaml
ports:
  - "8080:5000"  # Access at http://localhost:8080
```

---

## 🚀 Production Deployment

### Build for Production

```bash
# Build with specific tag
docker build -t thesis-recommender:1.0.0 .

# Run with production settings
docker run -d \
  --name thesis-recommender \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  --restart unless-stopped \
  thesis-recommender:1.0.0
```

### Using Docker Compose (Recommended)

```bash
# Production deployment
docker-compose up -d

# Scale if needed (future)
docker-compose up -d --scale thesis-recommender=3
```

---

## 📊 Data Persistence

### Initial Setup

Before first run, you need to populate the article store:

```bash
# Option 1: Run setup inside container
docker-compose run --rm thesis-recommender python populate_article_store.py

# Option 2: Run setup locally, then mount data/
python populate_article_store.py
docker-compose up -d
```

### Data Directory Structure

```
data/
├── articles.db      # Article metadata (SQLite)
├── faiss.index      # Vector embeddings (FAISS)
├── bm25.pkl         # BM25 index (Pickle)
├── feedback.db      # User ratings (SQLite)
└── users.db         # User accounts (SQLite)
```

---

## 🔍 Monitoring

### Health Checks

The container includes automatic health checks:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' hybrid-thesis-recommender | jq
```

### Logs

```bash
# Follow logs
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100

# View logs for specific service
docker-compose logs thesis-recommender
```

---

## 🛠️ Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Check if port is already in use
netstat -an | grep 5000

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Model Download Issues

If the embedding model fails to download during build:

```bash
# Build with increased timeout
docker-compose build --build-arg DOCKER_BUILDKIT=1

# Or download model manually first
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"
```

### Data Not Persisting

Ensure the `data/` directory exists and has correct permissions:

```bash
mkdir -p data
chmod 755 data
docker-compose down
docker-compose up -d
```

---

## 🔐 Security Considerations

### Production Checklist

- [ ] Change `SECRET_KEY` in `config.yaml`
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Restrict network access (firewall rules)
- [ ] Regular security updates: `docker-compose pull && docker-compose up -d`
- [ ] Backup `data/` directory regularly

### Reverse Proxy Example (Nginx)

```nginx
server {
    listen 80;
    server_name thesis-recommender.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📈 Performance Tuning

### Resource Limits

Add resource limits in `docker-compose.yml`:

```yaml
services:
  thesis-recommender:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Optimize for Large Datasets

For large article corpora (>100k articles):

1. Increase memory limit to 8GB+
2. Use SSD for `data/` volume
3. Consider using PostgreSQL instead of SQLite
4. Enable FAISS GPU support (requires CUDA)

---

## 🧪 Development Mode

### Run with Hot-Reload

```bash
# Mount source code for development
docker run -it --rm \
  -p 5000:5000 \
  -v $(pwd)/app:/app/app \
  -v $(pwd)/static:/app/static \
  -v $(pwd)/data:/app/data \
  thesis-recommender:latest \
  python -m app.main serve --debug
```

### Interactive Shell

```bash
# Access container shell
docker-compose exec thesis-recommender bash

# Run Python REPL
docker-compose exec thesis-recommender python
```

---

## 📦 Image Size

Expected image sizes:

- **Builder stage**: ~2.5 GB (includes build tools)
- **Final image**: ~1.8 GB (runtime only)
- **With model cached**: ~2.2 GB (includes embedding model)

To check image size:

```bash
docker images thesis-recommender
```

---

## 🔄 Updates and Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup Data

```bash
# Backup data directory
tar -czf thesis-recommender-backup-$(date +%Y%m%d).tar.gz data/

# Restore from backup
tar -xzf thesis-recommender-backup-20260503.tar.gz
```

### Clean Up

```bash
# Remove stopped containers
docker-compose down

# Remove images
docker rmi thesis-recommender:latest

# Clean up all unused Docker resources
docker system prune -a
```

---

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs`
- GitHub Issues: [Your Repository]
- Documentation: `README.md`

---

## ✅ Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] `config.yaml` configured
- [ ] `data/` directory populated with articles
- [ ] Ports 5000 available (or configured differently)
- [ ] Build successful: `docker-compose build`
- [ ] Container running: `docker-compose up -d`
- [ ] Health check passing: `docker ps`
- [ ] Application accessible: http://localhost:5000
- [ ] Logs clean: `docker-compose logs`

**Ready for production! 🚀**
