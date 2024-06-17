import threading
import time
from modules.posts_processing import PostProcessor
from modules.driver_utils import DriverUtils
import modules.shared as shared

class ThreadManager:
    def __init__(self, subreddit, num_threads, drivers, initial_scroll_position):
        self.subreddit = subreddit
        self.num_threads = num_threads
        self.drivers = drivers
        self.initial_scroll_position = initial_scroll_position
        self.threads = shared.threads if shared.threads else []

    def scroll_and_extract(self, driver, driver_index):
        if shared.scroll_position == 0:
            shared.scroll_position = self.initial_scroll_position

        if driver_index != 0:
            DriverUtils.access_subreddit(self.subreddit, driver)
        
        while shared.processed_posts_count < shared.max_post_number and not shared.terminate_event.is_set():
            with shared.scroll_mutex:
                driver.execute_script(f"window.scrollTo(0, {shared.scroll_position});")
                shared.scroll_position += self.initial_scroll_position
            time.sleep(2)
            posts = PostProcessor.extract_posts(driver)
            if posts is not None:
                PostProcessor.process_posts(posts, driver)

    def start_threads(self):
        for idx in range(self.num_threads):
            thread = threading.Thread(target=self.scroll_and_extract, args=(self.drivers[idx], idx))
            thread.start()
            self.threads.append(thread)

        print(f"Count of thread: {len(self.threads)}")
        print("Threads started!")
        shared.threads = self.threads

        print("Working...")

        for thread in shared.threads:
            thread.join()


       