import time
from modules.driver_utils import DriverUtils
from modules.config import Config
from modules.posts_processing import PostProcessor
import modules.shared as shared

class SubredditScraper:
    def __init__(self, driver):
        self.driver = driver

    def update_scraper(self, subreddit, max_posts):
        self.subreddit = subreddit
        shared.max_post_number = max_posts

    def scrape_subreddit(self):
        DriverUtils.access_subreddit(self.subreddit, self.driver)
        time.sleep(3)
        
        posts_collected = PostProcessor.process_posts(self.driver, min_posts=shared.max_post_number)

        print(f"Collected {posts_collected} posts.")
