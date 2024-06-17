import json
import os
import time

from selenium.webdriver.common.by import By
from modules.config import Config
from modules.driver_utils import DriverUtils
import modules.shared as shared

class PostProcessor:
    @staticmethod
    def write_post_to_json(title, author, content):
        post = {
            'Title': title,
            'Author': author,
            'Content': content
        }

        mode = 'a' if os.path.exists(Config.json_filename) else 'w'
        with open(Config.json_filename, mode, encoding='utf-8') as json_file:
            if mode == 'a':
                json_file.write(',\n')
            else:
                json_file.write('[\n')

            json.dump(post, json_file, ensure_ascii=False)

    @staticmethod
    def finalize_json_file():
        with open(Config.json_filename, 'a', encoding='utf-8') as json_file:
            json_file.write('\n]')

    @staticmethod
    def extract_posts(driver):
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                posts = driver.find_elements(By.CSS_SELECTOR, "article[aria-label]")
                return posts
            except Exception as e:
                if not DriverUtils.is_driver_alive(driver):
                    print("Driver is no longer alive. Terminating function.")
                    return None

                retry_count += 1
                if retry_count == max_retries:
                    print(f"Failed after {max_retries} attempts due to: {e}")
                    raise
                else:
                    print(f"Retrying ({retry_count}/{max_retries}) after exception: {e}")
                    time.sleep(2)

    @staticmethod
    def process_posts(posts, driver):
        
        for post in posts:
            try:
                title = post.find_element(By.CSS_SELECTOR, "a[href^='/r/']").text
                author = post.find_element(By.CSS_SELECTOR, "a[href^='/user/']").text[2:]

                content_element = post.find_element(By.CSS_SELECTOR, "div[id$='-post-rtjson-content']")
                post_content = content_element.text.strip() if content_element else ""

                with shared.recording_post_lock:
                    PostProcessor.write_post_to_json(title, author, post_content)

                with shared.processed_posts_lock:
                    shared.processed_posts_count += 1
                    if not shared.processed_posts_count % 20:
                        print(f"Processed posts: {shared.processed_posts_count}")

                if shared.processed_posts_count >= shared.max_post_number:
                    print(f"Processed {shared.processed_posts_count} posts. Terminating...")
                    shared.terminate_event.set()
                    return

            except Exception as e:
                if not DriverUtils.is_driver_alive(driver):
                    print("Driver is no longer alive. Terminating function.")
                    return None
