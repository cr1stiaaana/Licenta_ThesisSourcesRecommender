"""Properly populate ArticleStore with articles and embeddings."""

import numpy as np
from sentence_transformers import SentenceTransformer
from app.article_store import ArticleStore
from app.models import Article

print("Loading embedding model...")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

print("Initializing ArticleStore...")
store = ArticleStore(
    vector_store_path='data/faiss.index',
    metadata_db_path='data/articles.db'
)

articles = [
    Article(
        id='spec_1',
        title='Specification-Driven Development: A Practical Approach',
        abstract='This paper presents a methodology for specification-driven development where formal specifications guide the implementation process. We demonstrate how specifications can improve code quality and reduce bugs.',
        authors=['Smith, John', 'Johnson, Mary'],
        year=2020,
        doi=None,
        url='https://example.com/spec-driven',
        keywords=[],
        language='en'
    ),
    Article(
        id='spec_2',
        title='Test-Driven Development: By Example',
        abstract='Test-driven development (TDD) is a software development process that relies on the repetition of a very short development cycle. This book provides practical examples of TDD in action.',
        authors=['Beck, Kent'],
        year=2003,
        doi=None,
        url='https://example.com/tdd',
        keywords=[],
        language='en'
    ),
    Article(
        id='spec_3',
        title='Behavior-Driven Development with Cucumber',
        abstract='Behavior-driven development (BDD) is an extension of test-driven development that emphasizes collaboration between developers, QA, and non-technical participants. This paper explores BDD practices.',
        authors=['Wynne, Matt', 'Hellesoy, Aslak'],
        year=2017,
        doi=None,
        url='https://example.com/bdd',
        keywords=[],
        language='en'
    ),
    Article(
        id='spec_4',
        title='Formal Methods in Software Development',
        abstract='Formal methods use mathematical techniques to specify, develop, and verify software systems. This survey covers the state of the art in formal specification languages and verification tools.',
        authors=['Clarke, Edmund', 'Wing, Jeannette'],
        year=1996,
        doi=None,
        url='https://example.com/formal-methods',
        keywords=[],
        language='en'
    ),
    Article(
        id='spec_5',
        title='Property-Based Testing for Better Code',
        abstract='Property-based testing is a testing methodology where test cases are generated automatically based on properties that the code should satisfy. This approach complements specification-driven development.',
        authors=['Hughes, John', 'Claessen, Koen'],
        year=2011,
        doi=None,
        url='https://example.com/property-testing',
        keywords=[],
        language='en'
    ),
]

print(f"\nAdding {len(articles)} articles...")
for i, article in enumerate(articles, 1):
    text = article.title
    if article.abstract:
        text += " " + article.abstract
    
    embedding = model.encode(text)
    # Normalize embedding to unit length for cosine similarity
    embedding = embedding / np.linalg.norm(embedding)
    store.add_article(article, embedding)
    print(f"  {i}. {article.title}")

print("\n✅ Articles added successfully!")
print("Restart the server to see the changes.")
