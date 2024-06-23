import json
import os
import re
import threading
import time
import yaml
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from modules.driver_utils import DriverUtils
from modules.file_write_error import FileWriteError
from modules.colors import Colors
import modules.shared as shared


class PostProcessor:
    @staticmethod
    def get_thread_color():
        thread_id = threading.get_ident()
        if thread_id not in shared.thread_colors:
            # Assign a color to the thread if it doesn't have one
            colors = [Colors.RED, Colors.GREEN, Colors.BLUE]
            shared.thread_colors[thread_id] = colors[len(shared.thread_colors) % len(colors)]
        return shared.thread_colors[thread_id]

    @staticmethod
    def clean_value(value):
        lines = [line.strip() for line in value.splitlines()]
        clean_lines = [line for line in lines if line]
        return ' '.join(clean_lines)
    
    @staticmethod
    def clean_xml(value):
        
        # Replace characters not allowed in XML with XML entities
        value = value.replace('&', '&amp;')  # Replace '&' with '&amp;'
        value = value.replace('<', '&lt;')   # Replace '<' with '&lt;'
        value = value.replace('>', '&gt;')   # Replace '>' with '&gt;'
        # Add more replacements as necessary for other special characters

        # Optionally, remove any non-printable characters
        value = ''.join(ch for ch in value if ch.isprintable())

        return value.strip()  # Strip leading/trailing whitespace  
       
    @staticmethod
    def write_post_to_file(data):
        file_path = shared.output_file_path
        thread_color = PostProcessor.get_thread_color()

        try:
            if shared.format_type == 'json':
                mode = 'a' if os.path.exists(file_path) else 'w'
                with open(file_path, mode, encoding='utf-8') as json_file:
                    if mode == 'a':
                        json_file.write(',\n')
                    else:
                        json_file.write('[\n')
                    data['Content'] = PostProcessor.clean_value(data['Content'])
                    json.dump(data, json_file, ensure_ascii=False)
            elif shared.format_type == 'yaml':
                mode = 'a' if os.path.exists(file_path) else 'w'
                with open(file_path, mode, encoding='utf-8') as yaml_file:
                    yaml_file.write('---\n')
                    data['Content'] = PostProcessor.clean_value(data['Content'])
                    yaml.dump(data, yaml_file, default_flow_style=False, allow_unicode=True)
            elif shared.format_type == 'xml':
                # Check if the file already exists
                if os.path.exists(file_path):
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    if root is None:
                        root = ET.Element('posts')
                else:
                    root = ET.Element('posts')

                post_element = ET.SubElement(root, 'post')
                for key, value in data.items():
                    clean_value = PostProcessor.clean_xml(value)
                    ET.SubElement(post_element, key).text = clean_value

                tree = ET.ElementTree(root)
                with open(file_path, 'wb') as xml_file:
                    tree.write(xml_file, encoding='utf-8')

        except Exception as e:
            raise FileWriteError(f"{thread_color}Failed to write to file '{file_path}': {str(e)}{Colors.RESET}")

    @staticmethod
    def finalize_file():
        if shared.format_type not in ['json', 'yaml', 'xml']:
            raise ValueError(f"Invalid format type: {shared.format_type}")

        file_path = f"{shared.output_file_path}"

        if shared.format_type == 'json':
            with open(file_path, 'a', encoding='utf-8') as json_file:
                json_file.write('\n]')
        elif shared.format_type == 'yaml':
            pass
        elif shared.format_type == 'xml':
            pass

    @staticmethod
    def process_posts(driver):
        if shared.format_type not in ['json', 'yaml', 'xml']:
            raise ValueError(f"Invalid format type: {shared.format_type}")

        previous_html = None
        shared.processed_posts_count = 0

        max_trials = 4
        trials = 0

        terminate_processing = False
        thread_color = PostProcessor.get_thread_color()
        thread_id = threading.get_ident()

        while shared.processed_posts_count < shared.limit and not terminate_processing:
            DriverUtils.scroll_to_bottom(driver)
            new_html = DriverUtils.get_document_element(driver)

            if not DriverUtils.new_posts_loaded(previous_html, new_html):
                if trials < max_trials:
                    previous_html = new_html
                    trials += 1
                    if shared.verbose:
                        print(f"{thread_color}Thread {thread_id}: [{max_trials - trials}] Remaining scrolling trials.{Colors.RESET}")
                    time.sleep(trials)
                    continue

                if shared.verbose:
                    print(f"{thread_color}Thread {thread_id}: No new posts loaded. Terminating.{Colors.RESET}")
                break

            previous_html = new_html

            soup = BeautifulSoup(new_html, 'html.parser')
            post_containers = soup.find_all('article', {'class': 'w-full m-0'})

            for container in post_containers:
                if shared.processing_done:
                    break
                try:
                    title = container.get('aria-label', 'No title').strip()
                    author_element = container.find('a', href=lambda href: href and '/user/' in href)
                    author = author_element.text.strip() if author_element else "Unknown author"
                    content_div = container.find('div', id=lambda id: id and 'post-rtjson-content' in id)
                    content = content_div.get_text(separator='\n').strip() if content_div else "No content"

                    post_data = {
                        'Title': title,
                        'Author': author,
                        'Content': content
                    }

                    with shared.lock:
                        PostProcessor.write_post_to_file(post_data)
                        shared.processed_posts_count += 1

                    if shared.processed_posts_count >= shared.limit:
                        break
                except FileWriteError as e:
                    print(f"{thread_color}Thread {thread_id}: File write error occurred: {e}{Colors.RESET}")
                    terminate_processing = True
                    break
                except Exception as e:
                    print(f"{thread_color}Thread {thread_id}: Error processing post: {e}{Colors.RESET}")

            trials = 0

            if shared.verbose:
                print(f"{thread_color}Thread {thread_id}: Processed posts: {shared.processed_posts_count}{Colors.RESET}")

            if shared.processed_posts_count >= shared.limit:
                if shared.verbose:
                    print(f"{thread_color}Thread {thread_id}: Processed {shared.processed_posts_count} posts. Terminating...{Colors.RESET}")
                
                if not shared.processing_done:
                    shared.processing_done = True
                    PostProcessor.finalize_file()
                break

        return shared.processed_posts_count
