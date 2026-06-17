---
name: web-search-config
description: Configurare și switch între providerii de web search (DuckDuckGo, Google CSE, Bing).
version: 1.0.0
---

# Skill: Web Search Configuration

## Overview

This skill guides configuring and switching between web search providers (DuckDuckGo, Google CSE, Bing).

## Available Providers

| Provider | API Key Required | Rate Limits | Quality |
|----------|:----------------:|-------------|---------|
| **DuckDuckGo** | ❌ No | Soft (be polite) | Good |
| **Google CSE** | ✅ Yes | 100/day free | Excellent |
| **Bing Search** | ✅ Yes | 1000/month free | Excellent |

## Configuration (`config.yaml`)

```yaml
# Switch provider
web_search_provider: "duckduckgo"  # or "google_cse" or "bing"

# Number of results
web_search_num_results: 20

# Bilingual search (queries in both RO and EN)
bilingual_web_search: false

# Timeout per search request
web_search_timeout: 10
```

## DuckDuckGo (Default — No Setup Required)

Works out of the box. Uses the `ddgs` Python package.

```python
# No API key needed
# Just set in config.yaml:
web_search_provider: "duckduckgo"
```

**Limitations:**
- No official API (uses scraping-like approach)
- May get rate-limited with heavy use
- Results quality slightly lower than Google/Bing

## Google Custom Search Engine

### Setup Steps
1. Go to https://programmablesearchengine.google.com/
2. Create a new search engine (search the entire web)
3. Get your **Search Engine ID** (cx)
4. Go to https://console.cloud.google.com/apis/credentials
5. Create an **API Key**
6. Enable "Custom Search API" in the API library

### Configuration
```yaml
web_search_provider: "google_cse"
google_cse_api_key: "AIza..."
google_cse_cx: "a1b2c3..."
```

**Free tier:** 100 queries/day (enough for development/demo)

## Bing Search API

### Setup Steps
1. Go to https://portal.azure.com/
2. Create a "Bing Search v7" resource
3. Get your **API Key** from the resource keys

### Configuration
```yaml
web_search_provider: "bing"
bing_api_key: "abc123..."
```

**Free tier:** 1000 transactions/month

## Bilingual Search

When enabled, the system issues two parallel queries:
1. Original query in detected language
2. Same query translated/reformulated in the other language

Results are merged and deduplicated by URL.

```yaml
bilingual_web_search: true  # Doubles API usage
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No web results returned | Check internet connection, try different provider |
| Rate limited (DuckDuckGo) | Add delay between requests or switch to Google/Bing |
| Google API quota exceeded | Wait 24h or upgrade to paid tier |
| Timeout errors | Increase `web_search_timeout` in config |
| Irrelevant results | Try enabling `bilingual_web_search` for broader coverage |

## Testing

```bash
# Test web search independently
python test_web_search.py

# Test academic search (Semantic Scholar + arXiv)
python test_academic_search.py

# Test full system with web results
python test_full_system.py
```
