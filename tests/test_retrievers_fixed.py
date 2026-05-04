"""Test retrievers after rebuilding indexes."""

from app.article_store import ArticleStore
from app.config_manager import ConfigManager
from app.retrievers.semantic import SemanticRetriever
from app.retrievers.keyword import KeywordRetriever
from app.models import Query

print("Initializing components...")
config_manager = ConfigManager('config.yaml')
config = config_manager.get()

store = ArticleStore(
    vector_store_path=config.vector_store_path,
    metadata_db_path=config.metadata_db_path
)

semantic = SemanticRetriever(store, config)
keyword = KeywordRetriever(store, config)

query = Query(title="spec driven dev", abstract=None, keywords=[])

print("\n" + "="*60)
print("Testing SemanticRetriever...")
print("="*60)
sem_results = semantic.retrieve(query, top_k=5)
print(f"Results: {len(sem_results.items)}")
for i, item in enumerate(sem_results.items, 1):
    print(f"{i}. {item.article.title[:60]}... (score: {item.score:.3f})")

print("\n" + "="*60)
print("Testing KeywordRetriever...")
print("="*60)
kw_results = keyword.retrieve(query, top_k=5)
print(f"Results: {len(kw_results.items)}")
for i, item in enumerate(kw_results.items, 1):
    print(f"{i}. {item.article.title[:60]}... (score: {item.score:.3f})")

print("\n✅ Both retrievers working!")
