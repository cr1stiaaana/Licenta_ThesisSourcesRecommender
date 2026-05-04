"""
Contract tests for API endpoints based on OpenAPI specification.

These tests verify that the API implementation conforms to the OpenAPI spec:
- Request/response schemas
- Status codes
- Required fields
- Data types
- Validation rules
"""

import pytest
import yaml
from pathlib import Path


# Load OpenAPI spec
SPEC_PATH = Path(__file__).parent.parent / "openapi.yaml"
with open(SPEC_PATH, 'r', encoding='utf-8') as f:
    OPENAPI_SPEC = yaml.safe_load(f)


class TestRecommendEndpoint:
    """Test /recommend endpoint contract."""
    
    def test_recommend_success_response_structure(self, client):
        """Test that successful response matches OpenAPI schema."""
        response = client.post('/recommend', json={
            'title': 'machine learning neural networks',
            'offset': 0,
            'type': 'both'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify required fields from schema
        assert 'query_language' in data
        assert 'articles' in data
        assert 'web_resources' in data
        assert 'notices' in data
        
        # Verify types
        assert isinstance(data['query_language'], str)
        assert data['query_language'] in ['ro', 'en']
        assert isinstance(data['articles'], list)
        assert isinstance(data['web_resources'], list)
        assert isinstance(data['notices'], list)
    
    def test_recommend_article_schema(self, client):
        """Test that article recommendations match OpenAPI schema."""
        response = client.post('/recommend', json={
            'title': 'machine learning',
            'type': 'articles'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        if data['articles']:
            article = data['articles'][0]
            
            # Required fields
            assert 'resource_type' in article
            assert article['resource_type'] == 'article'
            assert 'title' in article
            assert 'score' in article
            assert 'item_id' in article
            
            # Optional fields with correct types
            if 'authors' in article:
                assert isinstance(article['authors'], list)
            if 'year' in article:
                assert isinstance(article['year'], (int, type(None)))
            if 'keywords' in article:
                assert isinstance(article['keywords'], list)
    
    def test_recommend_web_resource_schema(self, client):
        """Test that web resources match OpenAPI schema."""
        response = client.post('/recommend', json={
            'title': 'machine learning',
            'type': 'web'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        if data['web_resources']:
            resource = data['web_resources'][0]
            
            # Required fields
            assert 'resource_type' in resource
            assert resource['resource_type'] == 'web'
            assert 'title' in resource
            assert 'url' in resource
            assert 'web_score' in resource
            assert 'item_id' in resource
            
            # Verify types
            assert isinstance(resource['web_score'], (int, float))
            assert isinstance(resource['url'], str)
    
    def test_recommend_validation_error_422(self, client):
        """Test that invalid input returns 422 as per spec."""
        # Title too short (< 3 characters)
        response = client.post('/recommend', json={
            'title': 'ab'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert 'error' in data
    
    def test_recommend_pagination_parameters(self, client):
        """Test that pagination parameters work as specified."""
        # Test offset parameter
        response = client.post('/recommend', json={
            'title': 'machine learning',
            'offset': 5,
            'type': 'articles'
        })
        
        assert response.status_code == 200
        
        # Test type parameter
        for result_type in ['both', 'articles', 'web']:
            response = client.post('/recommend', json={
                'title': 'machine learning',
                'type': result_type
            })
            assert response.status_code == 200


class TestFeedbackEndpoint:
    """Test /feedback endpoints contract."""
    
    def test_submit_feedback_success(self, client):
        """Test successful feedback submission."""
        response = client.post('/feedback', json={
            'item_id': 'doi:10.1145/test',
            'query': 'machine learning',
            'rating': 5,
            'session_id': 'test-session-123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_submit_feedback_validation_rating_range(self, client):
        """Test that rating must be 1-5 as per spec."""
        # Rating too low
        response = client.post('/feedback', json={
            'item_id': 'doi:10.1145/test',
            'query': 'test',
            'rating': 0
        })
        assert response.status_code == 422
        
        # Rating too high
        response = client.post('/feedback', json={
            'item_id': 'doi:10.1145/test',
            'query': 'test',
            'rating': 6
        })
        assert response.status_code == 422
    
    def test_submit_feedback_required_fields(self, client):
        """Test that required fields are enforced."""
        # Missing item_id
        response = client.post('/feedback', json={
            'query': 'test',
            'rating': 5
        })
        assert response.status_code == 422
        
        # Missing query
        response = client.post('/feedback', json={
            'item_id': 'doi:10.1145/test',
            'rating': 5
        })
        assert response.status_code == 422
        
        # Missing rating
        response = client.post('/feedback', json={
            'item_id': 'doi:10.1145/test',
            'query': 'test'
        })
        assert response.status_code == 422
    
    def test_get_feedback_response_schema(self, client):
        """Test that GET /feedback/{item_id} matches schema."""
        # First submit a rating
        client.post('/feedback', json={
            'item_id': 'doi:10.1145/test-get',
            'query': 'test',
            'rating': 4,
            'session_id': 'test-session'
        })
        
        # Then retrieve it
        response = client.get('/feedback/doi:10.1145/test-get?session_id=test-session')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Required fields
        assert 'item_id' in data
        assert 'rating_count' in data
        
        # Optional fields with correct types
        if 'user_rating' in data:
            assert isinstance(data['user_rating'], (int, type(None)))
            if data['user_rating'] is not None:
                assert 1 <= data['user_rating'] <= 5
        
        if 'average_rating' in data:
            assert isinstance(data['average_rating'], (float, type(None)))


class TestAuthenticationEndpoints:
    """Test authentication endpoints contract."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/auth/register', json={
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'message' in data
        assert 'user' in data
        assert 'id' in data['user']
        assert 'username' in data['user']
    
    def test_register_validation_username_length(self, client):
        """Test that username must be at least 3 characters."""
        response = client.post('/auth/register', json={
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 422
    
    def test_register_validation_password_length(self, client):
        """Test that password must be at least 6 characters."""
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '12345'
        })
        
        assert response.status_code == 422
    
    def test_login_success(self, client):
        """Test successful login."""
        # First register
        client.post('/auth/register', json={
            'username': 'logintest',
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        # Then login
        response = client.post('/auth/login', json={
            'username': 'logintest',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'user' in data
    
    def test_login_invalid_credentials(self, client):
        """Test that invalid credentials return 401."""
        response = client.post('/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 401
    
    def test_logout_success(self, client):
        """Test successful logout."""
        response = client.post('/auth/logout')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_get_current_user(self, client):
        """Test GET /auth/me endpoint."""
        response = client.get('/auth/me')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data


class TestSavedItemsEndpoints:
    """Test saved items endpoints contract."""
    
    def test_get_saved_items_unauthenticated(self, client):
        """Test that GET /saved requires authentication."""
        response = client.get('/saved')
        assert response.status_code == 401
    
    def test_save_item_unauthenticated(self, client):
        """Test that POST /saved requires authentication."""
        response = client.post('/saved', json={
            'item_id': 'doi:10.1145/test',
            'item_data': {'title': 'Test'}
        })
        assert response.status_code == 401
    
    def test_save_item_validation(self, client):
        """Test that save item validates required fields."""
        # Register and login first
        client.post('/auth/register', json={
            'username': 'savetest',
            'email': 'save@example.com',
            'password': 'password123'
        })
        client.post('/auth/login', json={
            'username': 'savetest',
            'password': 'password123'
        })
        
        # Missing item_id
        response = client.post('/saved', json={
            'item_data': {'title': 'Test'}
        })
        assert response.status_code == 422
        
        # Missing item_data
        response = client.post('/saved', json={
            'item_id': 'doi:10.1145/test'
        })
        assert response.status_code == 422


class TestOpenAPISpecCompliance:
    """Test overall OpenAPI spec compliance."""
    
    def test_all_endpoints_defined_in_spec(self):
        """Verify all endpoints are documented in OpenAPI spec."""
        paths = OPENAPI_SPEC['paths']
        
        expected_endpoints = [
            '/recommend',
            '/feedback',
            '/feedback/{item_id}',
            '/auth/register',
            '/auth/login',
            '/auth/logout',
            '/auth/me',
            '/saved',
            '/saved/{item_id}',
            '/saved/{item_id}/check'
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in paths, f"Endpoint {endpoint} not documented in OpenAPI spec"
    
    def test_spec_version(self):
        """Test that OpenAPI version is 3.0.x."""
        assert OPENAPI_SPEC['openapi'].startswith('3.0')
    
    def test_spec_has_required_info(self):
        """Test that spec has required info fields."""
        info = OPENAPI_SPEC['info']
        assert 'title' in info
        assert 'version' in info
        assert 'description' in info
    
    def test_spec_has_servers(self):
        """Test that spec defines servers."""
        assert 'servers' in OPENAPI_SPEC
        assert len(OPENAPI_SPEC['servers']) > 0


# Pytest fixtures
@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    from app.config_manager import ConfigManager
    from app.api import create_app
    import tempfile
    import os
    
    # Create temporary directory for test databases
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test config
        test_config_path = os.path.join(tmpdir, 'test_config.yaml')
        with open(test_config_path, 'w') as f:
            f.write(f"""
semantic_weight: 0.6
keyword_weight: 0.4
article_top_k: 5
web_top_k: 5
semantic_top_k: 20
keyword_top_k: 20
min_article_score: 0.001
min_web_score: 0.05
embedding_model: "paraphrase-multilingual-mpnet-base-v2"
vector_store_path: "{tmpdir}/faiss.index"
metadata_db_path: "{tmpdir}/articles.db"
bm25_index_path: "{tmpdir}/bm25.pkl"
feedback_store_path: "{tmpdir}/feedback.db"
user_store_path: "{tmpdir}/users.db"
secret_key: "test-secret-key"
web_search_provider: "duckduckgo"
web_search_num_results: 50
bilingual_web_search: false
default_language: "en"
restrict_language: null
request_timeout_seconds: 20.0
component_timeout_seconds: 18.0
mismatch_threshold: 0.3
domain_blocklist: []
feedback_signal_enabled: false
feedback_signal_boost: 0.1
feedback_signal_min_rating: 4.0
fusion_strategy: "rrf"
""")
        
        config_manager = ConfigManager(test_config_path)
        app = create_app(config_manager)
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            yield client
