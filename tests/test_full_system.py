"""Test the full system without running the server (simulates what the server will do)."""

from app.config_manager import ConfigManager
from app.article_store import ArticleStore
from app.retrievers.semantic import SemanticRetriever
from app.retrievers.keyword import KeywordRetriever
from app.retrievers.web import WebRetriever
from app.retrievers.academic_web import AcademicWebRetriever
from app.rankers.hybrid import HybridRanker
from app.feedback.store import FeedbackStore
from app.models import Query
import concurrent.futures

print("="*70)
print("FULL SYSTEM TEST (simulates /recommend endpoint)")
print("="*70)

# Initialize all components (same as create_app)
print("\n1. Initializing components...")
config_manager = ConfigManager('config.yaml')
config = config_manager.get()

article_store = ArticleStore(
    vector_store_path=config.vector_store_path,
    metadata_db_path=config.metadata_db_path
)

semantic_retriever = SemanticRetriever(article_store, config)
keyword_retriever = KeywordRetriever(article_store, config)
web_retriever = WebRetriever(config)
academic_web_retriever = AcademicWebRetriever(timeout=config.component_timeout_seconds)
feedback_store = FeedbackStore(config.feedback_store_path)
hybrid_ranker = HybridRanker(config, feedback_store=feedback_store)

print("   ✓ All components initialized")

# Create query
query = Query(title="spec driven dev", abstract=None, keywords=[])
print(f"\n2. Query: '{query.title}'")

# Run retrievers in parallel (same as endpoint)
print("\n3. Running retrievers in parallel...")
semantic_result = None
keyword_result = None
academic_web_result = None
web_result = None

timeout = config.component_timeout_seconds

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        "semantic": executor.submit(semantic_retriever.retrieve, query, config.semantic_top_k),
        "keyword": executor.submit(keyword_retriever.retrieve, query, config.keyword_top_k),
        "academic_web": executor.submit(academic_web_retriever.retrieve, query, config.article_top_k),
        "web": executor.submit(web_retriever.retrieve, query, "en"),
    }
    
    for name, future in futures.items():
        try:
            result = future.result(timeout=timeout)
            if name == "semantic":
                semantic_result = result
                print(f"   ✓ SemanticRetriever: {len(result.items)} results")
            elif name == "keyword":
                keyword_result = result
                print(f"   ✓ KeywordRetriever: {len(result.items)} results")
            elif name == "academic_web":
                academic_web_result = result
                print(f"   ✓ AcademicWebRetriever: {len(result.items)} results")
            elif name == "web":
                web_result = result
                print(f"   ✓ WebRetriever: {len(result.items)} results")
        except Exception as exc:
            print(f"   ✗ {name} failed: {exc}")

# Merge academic_web with semantic
if academic_web_result and academic_web_result.items:
    if semantic_result:
        semantic_result.items.extend(academic_web_result.items)
    else:
        semantic_result = academic_web_result

# Fuse articles
print("\n4. Fusing articles with HybridRanker...")
from app.models import RetrievalResult
sem = semantic_result if semantic_result else RetrievalResult(source="semantic")
kw = keyword_result if keyword_result else RetrievalResult(source="keyword")

articles = hybrid_ranker.fuse_articles(
    semantic=sem,
    keyword=kw,
    top_k=config.article_top_k,
    semantic_weight=config.semantic_weight,
    keyword_weight=config.keyword_weight,
)
print(f"   ✓ Fused to {len(articles)} articles")

# Rank web resources
print("\n5. Ranking web resources...")
web_resources = hybrid_ranker.rank_web_resources(
    web=web_result if web_result else RetrievalResult(source="web"),
    top_k=config.web_top_k,
)
print(f"   ✓ Ranked to {len(web_resources)} web resources")

# Display results
print("\n" + "="*70)
print("RESULTS")
print("="*70)

print(f"\n📚 ARTICLES ({len(articles)}):")
if articles:
    for i, article in enumerate(articles, 1):
        print(f"   {i}. {article.title[:60]}...")
        print(f"      Score: {article.score:.3f}")
else:
    print("   ❌ No articles found!")

print(f"\n🌐 WEB RESOURCES ({len(web_resources)}):")
if web_resources:
    for i, resource in enumerate(web_resources, 1):
        print(f"   {i}. {resource.title[:60]}...")
        print(f"      Score: {resource.web_score:.3f}")
else:
    print("   ⚠️  No web resources found")

print("\n" + "="*70)
if articles and len(articles) >= 3:
    print("✅ SUCCESS! System is working correctly.")
    print("📌 Restart the Flask server to see these results in the UI.")
else:
    print("❌ ISSUE: Not enough articles returned.")
    print("   Expected at least 3 articles, got", len(articles))
print("="*70)
