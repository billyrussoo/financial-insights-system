import os
import json
import requests

# Algolia Product Hunt Search API credentials
ALGOLIA_APP_ID = "0H4SMABBSG"
ALGOLIA_API_KEY = "9670d2d619b9d07859448d7628eea5f3"
ALGOLIA_INDEX = "Post_production"

# Directory to save results
ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "../articles")
os.makedirs(ARTICLES_DIR, exist_ok=True)

def search_producthunt(keyword):
    url = f"https://{ALGOLIA_APP_ID.lower()}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}"
    headers = {
        "X-Algolia-API-Key": ALGOLIA_API_KEY,
        "X-Algolia-Application-Id": ALGOLIA_APP_ID
    }
    params = {"query": keyword}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        return results.get('hits', [])
    except requests.RequestException as e:
        print(f"❌ Error while searching Product Hunt for '{keyword}': {e}")
        return []

def format_post_summary(post):
    return {
        "name": post.get("name"),
        "tagline": post.get("tagline"),
        "url": post.get("url"),
        "votes": post.get("votesCount", 0)
    }

def save_producthunt_summary(keyword, posts):
    filename = f"producthunt_{keyword.lower()}.json"
    path = os.path.join(ARTICLES_DIR, filename)

    output = {
        "type": "producthunt_summary",
        "keyword": keyword,
        "results": posts if posts else "No results found."
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"✅ Saved: {filename}")

def run_producthunt_client(keywords):
    for keyword in keywords:
        print(f"🔍 Searching Product Hunt for: {keyword}")
        raw_posts = search_producthunt(keyword)
        formatted = [format_post_summary(post) for post in raw_posts[:20]]
        save_producthunt_summary(keyword, formatted)

# Example standalone test
if __name__ == "__main__":
    run_producthunt_client(["USA", "China", "Tariff"])
