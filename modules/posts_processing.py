import json
import os
import threading
import yaml
import threading
from time import sleep

from bs4 import BeautifulSoup

import xml.etree.ElementTree as ET

from modules.driver_utils import DriverUtils
from modules.file_write_error import FileWriteError
from modules.colors import Colors
from modules.core import RedditScraper
import modules.shared as shared


class PostProcessor:
    @staticmethod
    def get_thread_color():
        thread_id = threading.get_ident()
        if thread_id not in shared.thread_colors:
            # Assign a color to the thread if it doesn't have one
            colors = [Colors.RED, Colors.GREEN, Colors.BLUE]
            shared.thread_colors[thread_id] = colors[len(shared.thread_colors) % len(colors)]
        return thread_id, shared.thread_colors[thread_id]

    @staticmethod
    def add_dict_to_xml(element, data):
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(element, key)
                PostProcessor.add_dict_to_xml(child, value)
            elif isinstance(value, list):
                list_element = ET.SubElement(element, key)
                for item in value:
                    if isinstance(item, dict):
                        item_element = ET.SubElement(list_element, 'item')
                        PostProcessor.add_dict_to_xml(item_element, item)
                    else:
                        item_element = ET.SubElement(list_element, 'item')
                        item_element.text = PostProcessor.clean_xml(str(item))
            else:
                child = ET.SubElement(element, key)
                child.text = str(value)

           
    @staticmethod
    def write_post_to_file(data):
        def get_next_file_path(original_path, base_path, ext):
            base, current_ext = os.path.splitext(original_path)
            if current_ext:
                base_path = base

            index = 1
            while True:
                new_file_path = f"{base_path}_{index}.{ext}"
                if not os.path.exists(new_file_path):
                    return new_file_path
                index += 1

        def get_file_size(file_path):
            return os.path.getsize(file_path)

        file_path = shared.output_file_path
        _, thread_color = PostProcessor.get_thread_color()

        try:
            ext = shared.format_type.lower()

            if os.path.exists(file_path) and get_file_size(file_path) > 5 * 1024 * 1024:  # 5MB in bytes
                if shared.format_type == 'json':
                    with open(file_path, 'a', encoding='utf-8') as json_file:
                        json_file.write('\n]')
                file_path = get_next_file_path(shared.original_filepath_path, file_path, ext)
                shared.output_file_path = file_path

            if shared.format_type == 'json':
                mode = 'a' if os.path.exists(file_path) else 'w'
                with open(file_path, mode, encoding='utf-8') as json_file:
                    if mode == 'a' and os.path.getsize(file_path) > 0:
                        json_file.write(',\n')
                    else:
                        json_file.write('[\n')
                    json.dump(data, json_file, indent=4, ensure_ascii=False)
            elif shared.format_type == 'yaml':
                mode = 'a' if os.path.exists(file_path) else 'w'
                with open(file_path, mode, encoding='utf-8') as yaml_file:
                    yaml_file.write('---\n')
                    yaml.dump(data, yaml_file, default_flow_style=False, allow_unicode=True)

            elif shared.format_type == 'xml':
                if os.path.exists(file_path):
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    if root is None:
                        root = ET.Element('posts')
                else:
                    root = ET.Element('posts')

                post_element = ET.SubElement(root, 'post')
                PostProcessor.add_dict_to_xml(post_element, data)

                tree = ET.ElementTree(root)
                with open(file_path, 'wb') as xml_file:
                    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
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
    def divide_work(permalinks, drivers_number):
        # Calculate the size of each chunk
        chunk_size = len(permalinks) // drivers_number
        remainder = len(permalinks) % drivers_number

        # Initialize the result list
        divided_jobs = []
        start_index = 0

        # Create each chunk
        for i in range(drivers_number):
            end_index = start_index + chunk_size + (1 if i < remainder else 0)
            divided_jobs.append(permalinks[start_index:end_index])
            start_index = end_index

        return divided_jobs

    @staticmethod
    def validate_file_format():
        if shared.format_type not in ['json', 'yaml', 'xml']:
            raise ValueError(f"Invalid format type: {shared.format_type}")
   
    @staticmethod
    def worker(worker_driver, thread_color, thread_id, permalinks):
       
       scraper = RedditScraper(worker_driver)

       total_permalinks = len(permalinks)
       count = 0
       terminate_processing = False
       while count < total_permalinks and not terminate_processing:
           try:
               permalink = permalinks[count]

               if count == 0:
                 worker_driver.get(f'https://www.reddit.com{permalink}')
               else:
                 worker_driver.execute_script(f"window.open('https://www.reddit.com{permalink}', '_blank');")

               DriverUtils.accept_quarantined(worker_driver)

               windows = worker_driver.window_handles

               if len(windows) > 2:
                   worker_driver.switch_to.window(windows[1])
                   worker_driver.close()
                   windows = worker_driver.window_handles

               worker_driver.switch_to.window(windows[-1])
               post_data = scraper.scrape_post(worker_driver)

               with shared.lock:
                   if post_data and not shared.processing_done:
                        PostProcessor.write_post_to_file(post_data)
                        shared.processed_posts_count += 1
                        
                        if shared.processed_posts_count % 5 == 0:
                         print(f"{thread_color}Thread {thread_id}: Processed posts: {shared.processed_posts_count}{Colors.RESET}")

                        if shared.processed_posts_count >= shared.limit:
                            terminate_processing = True

               worker_driver.switch_to.window(windows[0])

               count += 1

           except Exception as e:
            #    print(f"{thread_color}Worker thread error: {e}{Colors.RESET}") #-------> For Debugging
            pass 
           
    @staticmethod
    def process_posts(driver, worker_drivers):
        
        PostProcessor.validate_file_format()

        previous_html = None

        max_trials = 4
        trials = 0


        terminate_processing = False
        thread_id, thread_color = PostProcessor.get_thread_color()
       
        while shared.processed_posts_count < shared.limit and not terminate_processing:
            DriverUtils.scroll_to_bottom(driver)
            new_html = DriverUtils.get_document_element(driver)

            if not DriverUtils.new_posts_loaded(previous_html, new_html):
                if trials < max_trials:
                    previous_html = new_html
                    trials += 1
                    if shared.verbose:
                        print(f"{thread_color}Thread {thread_id}: [{max_trials - trials}] Remaining scrolling trials.{Colors.RESET}")
                    sleep(trials)
                    continue

                if shared.verbose:
                    print(f"{thread_color}Thread {thread_id}: No new posts loaded. Terminating.{Colors.RESET}")
                break

            previous_html = new_html

            soup = BeautifulSoup(new_html, 'html.parser')
            post_containers = soup.find_all('article', {'class': 'w-full m-0'})

            permalinks = []

            for container in post_containers:
                if shared.processing_done:
                    terminate_processing = True
                    break
                try:
                    shreddit_post = container.find('shreddit-post')
                    permalink = shreddit_post.get('permalink', '')

                    post_id = shreddit_post.get("id")

                    if post_id in shared.processed_posts:
                        # Ignore this post as it's already processed
                        continue
                
                    # If the post_id is not in the processed_posts list, process the post
                    permalinks.append(permalink)
                    
                    # Add the post_id to the processed_posts list
                    shared.processed_posts.append(post_id)


                    if shared.processed_posts_count >= shared.limit:
                        break
                except Exception as e:
                    # print(f"{thread_color}Thread {thread_id}: Error extracting permalink: {e}{Colors.RESET}") -------> For Debugging
                    pass

            # Divide the job
            divided_jobs = PostProcessor.divide_work(permalinks=permalinks, drivers_number=len(worker_drivers))
            # Create and start worker threads
            threads = []
            for i, worker_driver in enumerate(worker_drivers):
                thread = threading.Thread(target=PostProcessor.worker, args=(worker_driver, thread_color, thread_id, divided_jobs[i]))
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

        if shared.verbose:
            print(f"{thread_color}Thread {thread_id}: Processed posts: {shared.processed_posts_count}{Colors.RESET}")

        if not shared.processing_done:
            shared.processing_done = True

        return shared.processed_posts_count


