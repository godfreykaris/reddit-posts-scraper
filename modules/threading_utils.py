import threading
import time
from modules.posts_processing import PostProcessor
from modules.driver_utils import DriverUtils
import modules.shared as shared

class ThreadManager:
    def __init__(self, subreddit, drivers, initial_scroll_position):
        self.subreddit = subreddit
        self.driver = drivers[0]
        self.initial_scroll_position = initial_scroll_position

    def scroll_and_extract(self):
        if shared.scroll_position == 0:
            shared.scroll_position = self.initial_scroll_position

        DriverUtils.access_subreddit(self.subreddit, self.driver)
        
        while shared.processed_posts_count < shared.max_post_number and not shared.terminate_event.is_set():
            with shared.scroll_mutex:
                self.driver.execute_script(f"window.scrollTo(0, {shared.scroll_position});")
                shared.scroll_position += self.initial_scroll_position
            time.sleep(2)
            posts = PostProcessor.extract_posts(self.driver)
            if posts is not None:
                PostProcessor.process_posts(posts, self.driver)

    def start_thread(self):
        thread = threading.Thread(target=self.scroll_and_extract)
        thread.start()
        shared.threads = [thread]
