"""Test the /recommend endpoint directly."""

import requests
import json

url = "http://127.0.0.1:5000/recommend"
data = {
    "title": "spec driven dev",
    "abstract": None,
    "keywords": []
}

print("Sending POST request to /recommend...")
print(f"Query: {data['title']}")

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"\nStatus code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Query language: {result.get('query_language')}")
        print(f"Articles: {len(result.get('articles', []))}")
        print(f"Web resources: {len(result.get('web_resources', []))}")
        print(f"Notices: {result.get('notices', [])}")
        
        if result.get('articles'):
            print("\nArticles:")
            for i, article in enumerate(result['articles'][:3], 1):
                print(f"  {i}. {article['title']} (score: {article.get('score', 0):.3f})")
        
        if result.get('web_resources'):
            print("\nWeb Resources:")
            for i, resource in enumerate(result['web_resources'][:3], 1):
                print(f"  {i}. {resource['title']} (score: {resource.get('web_score', 0):.3f})")
    else:
        print(f"\n❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to server. Is it running on http://127.0.0.1:5000?")
except Exception as e:
    print(f"\n❌ Error: {e}")
