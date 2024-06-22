import threading
import time
from modules.posts_processing import PostProcessor
from modules.driver_utils import DriverUtils
import modules.shared as shared

class ThreadManager:
    def __init__(self, subreddit, drivers, initial_scroll_position):
        """
        Initialize ThreadManager with subreddit, drivers, and initial scroll position.

        Args:
        - subreddit (str): Name of the subreddit to scrape.
        - drivers (list): List of WebDriver instances.
        - initial_scroll_position (int): Initial scroll position for scraping.
        """
        self.subreddit = subreddit  # Initialize subreddit name
        self.driver = drivers[0]  # Use the first WebDriver instance from the list
        self.initial_scroll_position = initial_scroll_position  # Initialize initial scroll position

    def scroll_and_extract(self):
        """
        Method to scroll through the subreddit page and extract posts.

        This method accesses the subreddit's page, scrolls down in a threaded manner, 
        and extracts posts using the PostProcessor class.

        The scrolling continues until the processed post count reaches the shared limit 
        or termination event is set.
        """
        if shared.scroll_position == 0:
            shared.scroll_position = self.initial_scroll_position  # Set initial scroll position if not already set

        DriverUtils.access_subreddit(self.subreddit, self.driver)  # Access the subreddit using the WebDriver

        while shared.processed_posts_count < shared.limit and not shared.terminate_event.is_set():
            with shared.scroll_mutex:
                # Execute JavaScript to scroll down
                self.driver.execute_script(f"window.scrollTo(0, {shared.scroll_position});")
                shared.scroll_position += self.initial_scroll_position  # Increment scroll position
            time.sleep(2)  # Wait for 2 seconds after scrolling
            posts = PostProcessor.extract_posts(self.driver)  # Extract posts using PostProcessor
            if posts is not None:
                PostProcessor.process_posts(posts, self.driver)  # Process extracted posts

    def start_thread(self):
        """
        Method to start a new thread for scrolling and extracting posts.

        This method initializes a new thread that executes the scroll_and_extract method.
        It updates the shared threads list with the started thread.
        """
        thread = threading.Thread(target=self.scroll_and_extract)  # Create a new thread
        thread.start()  # Start the thread
        shared.threads = [thread]  # Update the shared threads list with the started thread
