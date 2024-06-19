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
            post_containers = soup.find_all('div', {'id': '-post-rtjson-content'})

            for container in post_containers:
                try:
                    title_element = container.find_previous('span', class_='flex flex-col justify-center min-w-0 shrink py-[var(--rem6)]')
                    title = title_element.text.strip() if title_element else "No title"

                    content_paragraphs = container.find_all('p')
                    content = '\n'.join([p.text.strip() for p in content_paragraphs])

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

