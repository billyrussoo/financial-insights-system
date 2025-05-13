import os
import logging
from datetime import datetime, timezone
import praw
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Use refresh token for persistent login
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    refresh_token=os.getenv("REDDIT_REFRESH_TOKEN"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

reddit.read_only = True  # Enforce read-only mode

def test_reddit_connection():
    """Test Reddit API connectivity before proceeding."""
    try:
        next(reddit.subreddit("all").hot(limit=1))
        logging.info("[✅] Reddit API connection successful.")
    except Exception as e:
        logging.error(f"[❌] Reddit API connection failed: {e}")

def search_reddit(keyword, limit=10):
    logging.info(f"Searching Reddit for keyword: {keyword}")
    results = []
    try:
        for submission in reddit.subreddit("all").search(keyword, limit=limit, sort="relevance"):
            results.append({
                "id": submission.id,
                "title": submission.title,
                "subreddit": submission.subreddit.display_name,
                "score": submission.score,
                "created_utc": datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat(),
                "url": submission.url,
                "permalink": f"https://reddit.com{submission.permalink}",
                "selftext": submission.selftext
            })
    except Exception as e:
        logging.error(f"[❌] Reddit search failed for '{keyword}': {e}")
    return results

def get_social_trends(keywords, limit=50):
    logging.info(f"Analyzing social trends for keywords: {keywords}")
    trend_data = []

    for keyword in keywords:
        posts = search_reddit(keyword, limit=limit)
        count = len(posts)
        avg_score = sum(post['score'] for post in posts) / count if count else 0
        top_titles = [post['title'] for post in sorted(posts, key=lambda x: x['score'], reverse=True)[:3]]

        trend_data.append({
            "keyword": keyword,
            "post_count": count,
            "average_score": round(avg_score, 2),
            "top_titles": top_titles
        })

    return trend_data

if __name__ == "__main__":
    print("\n[🔧] Reddit Client Test")
    test_reddit_connection()
    test_keywords = ["AWS", "DevOps", "cloud computing"]
    trends = get_social_trends(test_keywords, limit=10)

    for trend in trends:
        print(f"\n🟢 Trend Summary for '{trend['keyword']}':")
        print(f"  Posts: {trend['post_count']}")
        print(f"  Avg Score: {trend['average_score']}")
        print("  Top Titles:")
        for title in trend["top_titles"]:
            print(f"   - {title}")
