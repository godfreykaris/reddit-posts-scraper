import json
import time
import os
from selenium.webdriver.common.by import By
from modules.config import Config
from modules.driver_utils import DriverUtils
from bs4 import BeautifulSoup
import modules.shared as shared

class PostProcessor:
    @staticmethod
    def write_post_to_json(title, content):
        post = {
            'Title': title,
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
    def process_posts(driver, min_posts=3000):
        previous_html = None

        shared.processing_started = True

        while shared.processed_posts_count < min_posts:
            DriverUtils.scroll_to_bottom(driver)
            new_html = DriverUtils.get_document_element(driver)

            if not DriverUtils.new_posts_loaded(previous_html, new_html):
                print("No new posts loaded. Terminating.")
                break
            
            previous_html = new_html

            soup = BeautifulSoup(new_html, 'html.parser')
            post_containers = soup.find_all('article', {'class': 'w-full m-0'})

            for container in post_containers:
                try:
                    # Extract title
                    title = container.get('aria-label', 'No title').strip()

                    # Extract author
                    author_element = container.find('a', href=lambda href: href and '/user/' in href)
                    author = author_element.text.strip() if author_element else "Unknown author"

                    # Extract content
                    content_div = container.find('div', id=lambda id: id and 'post-rtjson-content' in id)
                    content = content_div.get_text(separator='\n').strip() if content_div else "No content"

                    # Write post to JSON
                    PostProcessor.write_post_to_json(title, content)

                    shared.processed_posts_count += 1
                    if shared.processed_posts_count >= min_posts:
                        break

                except Exception as e:
                    print(f"Error processing post: {e}")

            if shared.processed_posts_count >= shared.max_post_number:
                print(f"Processed {shared.processed_posts_count} posts. Terminating...")
                shared.terminate_event.set()
                break

        PostProcessor.finalize_json_file()
        shared.processing_completed = True
        return shared.processed_posts_count

