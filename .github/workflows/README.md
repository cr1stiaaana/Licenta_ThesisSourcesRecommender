# GitHub Actions Workflows

Acest director conține workflow-urile GitHub Actions pentru CI/CD.

## 📋 Workflows Disponibile

### 1. `ci.yml` - Continuous Integration

**Trigger:** Push pe `main` sau `develop`, Pull Requests

**Jobs:**
- ✅ **test**: Rulează pytest și linting
- ✅ **build-docker**: Build Docker image și testează
- ✅ **deploy**: Notificare deployment (doar pe `main`)

**Status:** Rulează automat la fiecare push/PR

### 2. `docker-publish.yml` - Docker Image Publishing

**Trigger:** 
- Push tag-uri `v*.*.*` (ex: `v1.0.0`)
- Manual trigger (workflow_dispatch)

**Jobs:**
- ✅ Build Docker image
- ✅ Push la GitHub Container Registry (ghcr.io)
- ✅ Tag-uri automate (version, sha)

**Status:** Rulează la tag-uri sau manual

---

## 🚀 Cum să folosești

### CI/CD Automat

Workflow-ul `ci.yml` rulează automat:

```bash
# Push pe main → rulează toate job-urile
git push origin main

# Push pe develop → rulează test + build
git push origin develop

# Pull Request → rulează test + build
gh pr create
```

### Publish Docker Image

Pentru a publica o imagine Docker:

```bash
# Creează un tag
git tag v1.0.0
git push origin v1.0.0

# Sau rulează manual din GitHub UI:
# Actions → Docker Build and Push → Run workflow
```

Imaginea va fi disponibilă la:
```
ghcr.io/cr1stiaaana/licenta_thesissourcesrecommender:v1.0.0
```

---

## 📊 Status Badges

Adaugă în `README.md`:

```markdown
![CI/CD](https://github.com/cr1stiaaana/Licenta_ThesisSourcesRecommender/actions/workflows/ci.yml/badge.svg)
![Docker](https://github.com/cr1stiaaana/Licenta_ThesisSourcesRecommender/actions/workflows/docker-publish.yml/badge.svg)
```

---

## 🔧 Configurare

### Secrets Necesare

GitHub Actions folosește `GITHUB_TOKEN` automat (nu trebuie configurat).

Pentru deployment în cloud (opțional):
- `DOCKER_HUB_USERNAME` - Docker Hub username
- `DOCKER_HUB_TOKEN` - Docker Hub access token
- `AWS_ACCESS_KEY_ID` - AWS credentials (dacă deploy pe AWS)
- `AWS_SECRET_ACCESS_KEY` - AWS secret

Adaugă secrets în: **Settings → Secrets and variables → Actions**

---

## 📦 Cache

Workflow-urile folosesc cache pentru:
- ✅ Python dependencies (`pip cache`)
- ✅ Docker layers (`type=gha`)

Acest lucru accelerează build-urile cu ~50%.

---

## 🐛 Troubleshooting

### Tests fail

```bash
# Rulează local pentru debugging
pytest tests/ -v
```

### Docker build fail

```bash
# Testează local
docker build -t test .
```

### Permission denied la push image

Verifică că `GITHUB_TOKEN` are permisiuni:
- Settings → Actions → General → Workflow permissions → **Read and write permissions**

---

## 📚 Documentație

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

## ✅ Checklist

- [ ] Workflows create în `.github/workflows/`
- [ ] Push la GitHub
- [ ] Verifică tab "Actions" pe GitHub
- [ ] Testează un push pe `main`
- [ ] Verifică că build-ul trece
- [ ] (Opțional) Creează un tag pentru Docker publish

**Gata! CI/CD automat funcționează! 🎉**
