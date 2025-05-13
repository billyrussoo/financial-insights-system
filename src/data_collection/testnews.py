
from newsapi_client import fetch_news_articles

if __name__ == "__main__":
    keywords = input("Enter keywords for news search: ")
    news = fetch_news_articles(keywords)

    for i, article in enumerate(news, 1):
        print(f"\n[{i}] {article['title']}")
        print(f"Source: {article['source']}")
        print(f"URL: {article['url']}")
        print(f"Published At: {article['publishedAt']}")
        print(f"Description: {article['description']}")
        print(f"Full Text:\n{article['full_text'][:500]}...")  # Print first 500 chars of article text
