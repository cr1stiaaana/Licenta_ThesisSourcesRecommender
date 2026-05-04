"""Test web search functionality."""

from app.config_manager import ConfigManager
from app.retrievers.web import WebRetriever
from app.models import Query

print("Loading config...")
config_manager = ConfigManager('config.yaml')
cfg = config_manager.get()

print(f"Web search provider: {cfg.web_search_provider}")
print(f"Web search num results: {cfg.web_search_num_results}")

print("\nInitializing WebRetriever...")
web_retriever = WebRetriever(cfg)

print("\nSearching for 'spec driven dev'...")
query = Query(title="spec driven dev", abstract=None, keywords=[])

try:
    result = web_retriever.retrieve(query, query_language="en")
    print(f"\n✅ Found {len(result.items)} web resources:")
    for i, item in enumerate(result.items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   URL: {item.url}")
        print(f"   Score: {item.web_score:.3f}")
        if item.snippet:
            print(f"   Snippet: {item.snippet[:100]}...")
except Exception as e:
    print(f"\n❌ Web search failed: {e}")
    import traceback
    traceback.print_exc()
