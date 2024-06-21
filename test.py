import praw
import time

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id='UTUX12VDlo0_INa5l9VeYw',
    client_secret='UpKCDTMnbSPfnW3BIzMTCdgxZGi5dg',
    user_agent='Posts Retriever/0.1 by karis_Godfrey'
)

def fetch_latest_posts(subreddit_name, after=None):
    subreddit = reddit.subreddit(subreddit_name)
    if after:
        new_posts = list(subreddit.new(limit=500, params={'after': after}))
    else:
        new_posts = list(subreddit.new(limit=500))
    
    return new_posts

# Initial fetch
latest_posts = fetch_latest_posts('python')
if latest_posts:
    latest_post_id = latest_posts[-1].fullname  # Use fullname instead of id
    print(f"Fetched {len(latest_posts)} posts. Latest post ID: {latest_post_id}")

# Subsequent fetches
while True:
    latest_posts = fetch_latest_posts('python', after=latest_post_id)
    if latest_posts:
        latest_post_id = latest_posts[-1].fullname  # Use fullname instead of id
        print(f"Fetched {len(latest_posts)} posts. Latest post ID: {latest_post_id}")
    else:
        print("No new posts.")
    
    # Wait for some time before the next fetch
    time.sleep(20)