import time
import threading
from modules.threading_utils import ThreadManager
from modules.driver_utils import DriverUtils
from modules.config import Config
import modules.shared as shared

class SubredditScraper:
    def __init__(self, drivers, num_threads):
        self.drivers = drivers
        self.num_threads = num_threads

    def update_scraper(self, subreddit, max_posts):
        self.subreddit = subreddit
        shared.max_post_number = max_posts

    def scrape_subreddit(self):
        DriverUtils.access_subreddit(self.subreddit, self.drivers[0])
        time.sleep(3)
        initial_scroll_position = DriverUtils.get_initial_scroll_position(self.drivers[0])

        while initial_scroll_position == 0:
            initial_scroll_position = DriverUtils.get_initial_scroll_position(self.drivers[0])

        thread_manager = ThreadManager(self.subreddit, self.num_threads, self.drivers, initial_scroll_position)
        thread_manager.start_threads()

        for driver in shared.drivers:
            driver.quit()

        print(f"Total processed posts: {shared.processed_posts_count}")
