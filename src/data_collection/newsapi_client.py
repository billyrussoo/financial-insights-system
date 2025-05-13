import os
import requests
from dotenv import load_dotenv
from newspaper import Article

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news_articles(keywords, max_results=50):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": keywords,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": max_results,
        "sortBy": "relevancy",
    }
    response = requests.get(url, params=params)
    data = response.json()
    articles = data.get("articles", [])
    results = []

    for idx, article in enumerate(articles):
        full_text = extract_full_article(article["url"])
        results.append({
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "source": article["source"]["name"],
            "publishedAt": article["publishedAt"],
            "full_text": full_text
        })

    return results

def extract_full_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"[❌] Failed to extract article at {url}: {e}")
        return ""
