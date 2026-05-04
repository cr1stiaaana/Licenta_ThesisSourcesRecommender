"""Test if semantic and keyword retrievers work."""

from app.config_manager import ConfigManager
from app.article_store import ArticleStore
from app.retrievers.semantic import SemanticRetriever
from app.retrievers.keyword import KeywordRetriever
from app.models import Query

print("Loading config...")
config_manager = ConfigManager('config.yaml')
cfg = config_manager.get()

print("\nInitializing ArticleStore...")
try:
    article_store = ArticleStore(
        vector_store_path=cfg.vector_store_path,
        metadata_db_path=cfg.metadata_db_path
    )
    print(f"✅ ArticleStore initialized")
except Exception as e:
    print(f"❌ ArticleStore failed: {e}")
    exit(1)

print("\nInitializing SemanticRetriever...")
try:
    semantic_retriever = SemanticRetriever(article_store, cfg)
    print("✅ SemanticRetriever initialized")
except Exception as e:
    print(f"❌ SemanticRetriever failed: {e}")
    semantic_retriever = None

print("\nInitializing KeywordRetriever...")
try:
    keyword_retriever = KeywordRetriever(article_store, cfg)
    print("✅ KeywordRetriever initialized")
except Exception as e:
    print(f"❌ KeywordRetriever failed: {e}")
    keyword_retriever = None

# Test retrieval
query = Query(title="spec driven dev", abstract=None, keywords=[])

if semantic_retriever:
    print("\n" + "="*50)
    print("Testing SemanticRetriever...")
    print("="*50)
    try:
        result = semantic_retriever.retrieve(query, top_k=5)
        print(f"Found {len(result.items)} articles")
        for i, item in enumerate(result.items, 1):
            print(f"{i}. {item.article.title} (score: {item.score:.3f})")
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")

if keyword_retriever:
    print("\n" + "="*50)
    print("Testing KeywordRetriever...")
    print("="*50)
    try:
        result = keyword_retriever.retrieve(query, top_k=5)
        print(f"Found {len(result.items)} articles")
        for i, item in enumerate(result.items, 1):
            print(f"{i}. {item.article.title} (score: {item.score:.3f})")
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
