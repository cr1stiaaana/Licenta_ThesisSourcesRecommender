# API Documentation

This document describes how to use the OpenAPI specification for the Hybrid Thesis Recommender API.

## OpenAPI Specification

The complete API specification is available in `openapi.yaml` following the OpenAPI 3.0.3 standard.

## Viewing the API Documentation

### Option 1: Swagger UI (Recommended)

1. **Online Swagger Editor**:
   - Go to https://editor.swagger.io/
   - Click "File" → "Import file"
   - Select `openapi.yaml`
   - View interactive documentation with "Try it out" functionality

2. **Local Swagger UI** (Docker):
   ```bash
   docker run -p 8080:8080 -e SWAGGER_JSON=/openapi.yaml -v $(pwd)/openapi.yaml:/openapi.yaml swaggerapi/swagger-ui
   ```
   Then open http://localhost:8080

### Option 2: Redoc

```bash
docker run -p 8080:80 -e SPEC_URL=openapi.yaml -v $(pwd)/openapi.yaml:/usr/share/nginx/html/openapi.yaml redocly/redoc
```
Then open http://localhost:8080

### Option 3: VS Code Extension

Install the "OpenAPI (Swagger) Editor" extension and open `openapi.yaml` for syntax highlighting and validation.

## API Endpoints Overview

### Recommendations
- `POST /recommend` - Get hybrid recommendations with pagination support

### Feedback
- `POST /feedback` - Submit a rating (1-5 stars)
- `GET /feedback/{item_id}` - Get ratings for an item

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user

### Saved Items
- `GET /saved` - Get all saved items
- `POST /saved` - Save an item
- `DELETE /saved/{item_id}` - Remove saved item
- `GET /saved/{item_id}/check` - Check if item is saved

## Example Requests

### Get Recommendations

```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Neural networks for natural language processing",
    "abstract": "This thesis explores deep learning applications...",
    "keywords": ["machine learning", "NLP", "transformers"],
    "offset": 0,
    "type": "both"
  }'
```

### Submit Rating

```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "doi:10.1145/351240.351266",
    "query": "machine learning",
    "rating": 5,
    "session_id": "b8ba8da5-5b11-45b3-8dc1-135de4d37cf1"
  }'
```

### Register User

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

## Pagination

The `/recommend` endpoint supports independent pagination for articles and web resources:

- **Initial request**: `offset: 0, type: "both"` - Returns first 5 articles + 5 web resources
- **Load more articles**: `offset: 5, type: "articles"` - Returns next 5 articles
- **Load more web**: `offset: 5, type: "web"` - Returns next 5 web resources

## Response Codes

- `200` - Success
- `201` - Created (registration)
- `401` - Unauthorized (authentication required)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error (all retrievers unavailable)
- `503` - Service Unavailable (feedback store error)

## Authentication

The API uses session-based authentication with Flask sessions. After successful login/registration, a session cookie is set automatically.

## Code Generation

You can generate client SDKs from the OpenAPI spec:

### Python Client
```bash
openapi-generator-cli generate -i openapi.yaml -g python -o ./client-python
```

### JavaScript/TypeScript Client
```bash
openapi-generator-cli generate -i openapi.yaml -g typescript-axios -o ./client-ts
```

### Java Client
```bash
openapi-generator-cli generate -i openapi.yaml -g java -o ./client-java
```

## Validation

Validate the OpenAPI spec:

```bash
# Using Swagger CLI
swagger-cli validate openapi.yaml

# Using OpenAPI Generator
openapi-generator-cli validate -i openapi.yaml
```

## Integration with CI/CD

Add OpenAPI validation to your CI pipeline:

```yaml
# .github/workflows/api-validation.yml
name: API Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate OpenAPI Spec
        uses: char0n/swagger-editor-validate@v1
        with:
          definition-file: openapi.yaml
```

## Additional Resources

- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Redoc](https://redocly.com/redoc/)
- [OpenAPI Generator](https://openapi-generator.tech/)
