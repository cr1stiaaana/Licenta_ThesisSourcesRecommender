---
name: ollama-agent
description: Integrare AI agent local cu Ollama pentru query enhancement și sumarizare rezultate.
version: 1.0.0
---

# Skill: Ollama AI Agent Integration

## Overview

This skill guides the implementation of an AI agent powered by Ollama (local LLM) for query enhancement, result summarization, and conversational research assistance.

## Prerequisites

- Ollama installed locally (`ollama.com`)
- A model pulled: `ollama pull llama3.2` (3B, ~2GB) or `ollama pull mistral` (7B, ~4GB)
- Ollama running: `ollama serve` (default: `http://localhost:11434`)

## Architecture

```
User Query → Query Enhancement Agent (Ollama) → Enhanced Query
                                                      ↓
                                          Existing Pipeline
                                    (Semantic + BM25 + Web)
                                                      ↓
                                          Results → Summarization Agent (Ollama)
                                                      ↓
                                          Enriched Response to User
```

## Implementation Guide

### 1. Config Addition (`config.yaml`)

```yaml
agent:
  enabled: true
  provider: "ollama"
  base_url: "http://localhost:11434"
  model: "llama3.2"
  query_enhancement: true
  result_summarization: false
  timeout_seconds: 10
  max_retries: 2
```

### 2. Agent Module Location

```
app/
└── agents/
    ├── __init__.py
    ├── base.py              # Abstract base agent
    ├── ollama_client.py     # Ollama API client
    ├── query_agent.py       # Query enhancement
    └── summary_agent.py     # Result summarization
```

### 3. Key Implementation Details

- Use `requests` (already in requirements) to call Ollama API
- Endpoint: `POST http://localhost:11434/api/generate`
- Set `"stream": False` for simple request/response
- Timeout: 10s max (fallback to original query if agent fails)
- Agent is optional — system works without it (graceful degradation)

### 4. Integration Point

In `app/api.py`, the agent runs BEFORE the retrieval pipeline:
```python
if config.agent_enabled:
    enhanced = query_agent.enhance(original_query)
    # Use enhanced query for retrieval
else:
    # Use original query directly
```

### 5. Testing

```bash
# Test Ollama is running
curl http://localhost:11434/api/tags

# Test generation
curl http://localhost:11434/api/generate -d '{"model":"llama3.2","prompt":"hello","stream":false}'

# Test in project
python -c "from app.agents.ollama_client import OllamaClient; print(OllamaClient().generate('test'))"
```

## Prompts

### Query Enhancement Prompt
```
Given this thesis title: "{title}"

Generate a JSON object with:
- "keywords": 5 academic keywords related to this topic
- "reformulated": a more specific version of the title for academic search
- "alternatives": 3 alternative phrasings in English

Respond ONLY with valid JSON, no explanation.
```

### Result Explanation Prompt
```
Thesis: "{query}"
Article: "{article_title}" — {abstract_snippet}

In 1-2 sentences, explain the specific connection between this article and the thesis topic.
```

## Error Handling

- If Ollama is not running → skip agent, use original query
- If model not found → log warning, skip agent
- If timeout → skip agent, use original query
- Never let agent failure break the recommendation pipeline

## Recommended Models

| Model | Size | RAM Needed | Speed | Quality |
|-------|------|-----------|-------|---------|
| `llama3.2:3b` | 2GB | ~4GB | Fast | Good for keywords |
| `mistral:7b` | 4GB | ~8GB | Medium | Better reasoning |
| `phi3:mini` | 2.3GB | ~4GB | Fast | Good balance |
| `gemma2:2b` | 1.6GB | ~3GB | Very fast | Decent |
