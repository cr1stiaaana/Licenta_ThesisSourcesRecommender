# Hybrid Thesis Recommender API

**Version:** 1.0.0

REST API for an AI-powered academic research recommendation system that combines semantic search (FAISS), 
keyword matching (BM25), and multi-source web retrieval to provide relevant thesis sources.

## Features
- **Hybrid Retrieval**: Combines semantic embeddings with keyword matching
- **Multi-Source**: Integrates local corpus, Semantic Scholar, arXiv, and web search
- **User Feedback**: Rating system with optional feedback signal boosting
- **Authentication**: User registration, login, and saved items management
- **Bilingual**: Supports Romanian and English with automatic language detection
- **Content Verification**: Detects clickbait and low-quality sources


## Base URL

```
http://localhost:5000
```

## Endpoints


### POST /recommend

**Summary:** Get hybrid recommendations

Retrieves relevant articles and web resources using hybrid retrieval combining:
- Semantic search (FAISS with sentence-transformers)
- Keyword matching (BM25)
- Academic APIs (Semantic Scholar, arXiv)
- Web search (DuckDuckGo)

Supports pagination with independent offsets for articles and web resources.


**Tags:** Recommendations

**Request Body:**

```json
{
  // See OpenAPI spec for schema
}
```

**Responses:**

- `200`: Successful retrieval
- `422`: Invalid input (title validation failed)
- `500`: All retrievers unavailable


### POST /feedback

**Summary:** Submit a rating

Submit a user rating (1-5 stars) for an article or web resource

**Tags:** Feedback

**Request Body:**

```json
{
  // See OpenAPI spec for schema
}
```

**Responses:**

- `200`: Rating saved successfully
- `422`: Invalid input
- `503`: Feedback store unavailable


### GET /feedback/{item_id}

**Summary:** Get ratings for an item

Retrieve aggregate ratings and user's rating for a specific item

**Tags:** Feedback

**Responses:**

- `200`: Ratings retrieved successfully
- `503`: Feedback store unavailable


### POST /auth/register

**Summary:** Register a new user

Create a new user account

**Tags:** Authentication

**Request Body:**

```json
{
  // See OpenAPI spec for schema
}
```

**Responses:**

- `201`: Registration successful
- `400`: Registration failed (username/email already exists)
- `422`: Invalid input


### POST /auth/login

**Summary:** Login

Authenticate user and create session

**Tags:** Authentication

**Request Body:**

```json
{
  // See OpenAPI spec for schema
}
```

**Responses:**

- `200`: Login successful
- `401`: Invalid credentials
- `422`: Invalid input


### POST /auth/logout

**Summary:** Logout

Clear user session

**Tags:** Authentication

**Responses:**

- `200`: Logout successful


### GET /auth/me

**Summary:** Get current user

Retrieve currently authenticated user information

**Tags:** Authentication

**Responses:**

- `200`: User information or null if not authenticated


### GET /saved

**Summary:** Get saved items

Retrieve all saved items for the authenticated user

**Tags:** Saved Items

**Responses:**

- `200`: Saved items retrieved successfully
- `401`: Not authenticated


### POST /saved

**Summary:** Save an item

Save an article or web resource to user's collection

**Tags:** Saved Items

**Request Body:**

```json
{
  // See OpenAPI spec for schema
}
```

**Responses:**

- `200`: Item saved successfully
- `401`: Not authenticated
- `422`: Invalid input


### DELETE /saved/{item_id}

**Summary:** Remove saved item

Remove an item from user's saved collection

**Tags:** Saved Items

**Responses:**

- `200`: Item removed successfully
- `401`: Not authenticated


### GET /saved/{item_id}/check

**Summary:** Check if item is saved

Check whether a specific item is in user's saved collection

**Tags:** Saved Items

**Responses:**

- `200`: Check result

