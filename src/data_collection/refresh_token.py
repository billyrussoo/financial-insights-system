import praw
import os
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    redirect_uri=os.getenv("REDDIT_REDIRECT_URI"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Paste the code you got from the redirect
auth_code = input("Paste the code from the URL: ").strip()

# Exchange the code for a refresh token
refresh_token = reddit.auth.authorize(auth_code)
print(f"\n✅ Your permanent REFRESH TOKEN:\n{refresh_token}")
