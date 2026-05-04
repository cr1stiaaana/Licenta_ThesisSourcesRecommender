"""Test academic web retrieval for 'spec driven dev'."""

from app.retrievers.academic_web import AcademicWebRetriever
from app.models import Query

retriever = AcademicWebRetriever(timeout=15.0)
query = Query(title="spec driven dev", abstract=None, keywords=[])

print("Searching for: 'spec driven dev'")
print("-" * 50)

result = retriever.retrieve(query, top_k=10)

print(f"\nFound {len(result.items)} articles:")
print("-" * 50)

for i, scored_article in enumerate(result.items, 1):
    article = scored_article.article
    print(f"\n{i}. {article.title}")
    print(f"   Authors: {', '.join(article.authors) if article.authors else 'N/A'}")
    print(f"   Year: {article.year or 'N/A'}")
    print(f"   Score: {scored_article.score:.3f}")
    print(f"   URL: {article.url or 'N/A'}")
    if article.abstract:
        print(f"   Abstract: {article.abstract[:150]}...")
