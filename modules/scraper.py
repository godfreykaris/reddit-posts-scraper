import time
from modules.driver_utils import DriverUtils
from modules.config import Config
from modules.posts_processing import PostProcessor
import modules.shared as shared

class SubredditScraper:
    def __init__(self, driver):
        """
        Initialize SubredditScraper with a WebDriver instance.

        Args:
        - driver: Selenium WebDriver instance for web interaction.
        """
        self.driver = driver

    def update_scraper(self, limit):
        """
        Update the scraper's limit for the number of posts to scrape.

        Args:
        - limit (int): Maximum number of posts to scrape.
        """
        shared.limit = limit  # Update the shared limit variable

    def scrape_subreddit(self):
        """
        Perform scraping of a subreddit using the configured WebDriver instance.

        This method accesses the subreddit's page, waits for 3 seconds, 
        and collects posts using the PostProcessor class.

        It prints the total number of collected posts.
        """
        DriverUtils.access_subreddit(self.driver)  # Access the subreddit using the WebDriver

        PostProcessor.process_posts(self.driver)  # Process posts using PostProcessor
