import threading
import os
from modules.config import Config
from modules.posts_processing import PostProcessor
from modules.driver_utils import DriverUtils
from modules.scraper import SubredditScraper
import modules.shared as shared

class ThreadManager:
    def __init__(self, subreddit, category, limit, verbose, output_path):
        """
        Initialize ThreadManager with subreddit, category, limit, verbose mode, and output path.

        Args:
        - subreddit (str): Name of the subreddit to scrape.
        - category (str): Category to scrape ('hot', 'new', 'top').
        - limit (int): Limit on the number of posts to scrape.
        - verbose (bool): Enable verbose mode to print processing details.
        - output_path (str): Output file path for the scraped posts.
        """
        self.subreddit = subreddit
        self.category = category
        self.limit = limit
        self.verbose = verbose
        self.output_path = output_path

    def scrape_category(self):
        """
        Scrape posts from a specific category of subreddit.
        """
        try:
            print(f"Thread {threading.get_ident()}: Scraping {self.category} category....")
            DriverUtils.initialize_driver(self.category)

            # Set up shared variables
            shared.processed_posts_count = 0
            shared.limit = self.limit if self.limit is not None else float('inf')
            shared.scroll_position = 0
            shared.verbose = self.verbose
            shared.output_file_path = self.output_path

            shared.scraper = SubredditScraper(shared.drivers[self.category])
            Config.setup_output_file()

            shared.scraper.update_scraper(shared.limit)

            base_url = f"https://www.reddit.com/r/{self.subreddit}/"
            if self.category == "hot":
                shared.reddit_url = base_url + "hot/"
            elif self.category == "new":
                shared.reddit_url = base_url + "new/"
            elif self.category == "top":
                shared.reddit_url = base_url + "top/?t=all"
            else:
                print(f"Thread {threading.get_ident()}: Invalid category {self.category}. Skipping category.\n")
                return

            shared.scraper.scrape_subreddit()

        except Exception as e:
            #  print(f"Thread error: {e}") #-------> For Debugging
            pass

    def start_thread(self):
        """
        Method to start a new thread for scraping a category.

        This method initializes a new thread that executes the scrape_category method.
        It updates the shared threads list with the started thread.
        """
        thread = threading.Thread(target=self.scrape_category)
        thread.start()
        return thread

    def remove_existing_output_file(output_path):
        """
        Remove the output file if it exists

        Args:
        - output_path (str): Path to the output file.
        """
        if os.path.exists(output_path):
            os.remove(output_path)  # Remove the existing file if it exists
    
    def recreate_directory(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)