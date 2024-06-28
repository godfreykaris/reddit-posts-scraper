from random import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


class RedditScraper:
    def __init__(self, driver):
        self.driver = driver

    def expand_comment_thread(self):
        try:
            initial_scroll_height = self.driver.execute_script("return document.body.scrollHeight")

            while True:
                more_replies_spans = self.driver.find_elements(By.CSS_SELECTOR, 'span.text-secondary-weak.font-normal')

                for span in more_replies_spans:
                    if 'more replies' in span.text:
                        try:
                            parent_anchor = span.find_element(By.XPATH, './ancestor::a')
                            if parent_anchor and parent_anchor.get_attribute('href'):
                                # Skipping span with 'href' attribute to avoid redirect
                                continue
                        except Exception as e:
                            pass

                        self.driver.execute_script("arguments[0].scrollIntoView();", span)
                        self.driver.execute_script("arguments[0].click();", span)

                        # Wait for more replies to appear
                        time.sleep(random.uniform(2.0, 2.7))  # Random sleep between 3.0 and 4.5 seconds


                current_scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                if current_scroll_height == initial_scroll_height:
                    # Reached the bottom of the page.
                    break
                else:
                    initial_scroll_height = current_scroll_height
        except StaleElementReferenceException:
            # Stale element reference, retrying...
            self.expand_comment_thread()

        except Exception as e:
            # print(f"Error expanding comment thread: {str(e)}") -------> For Debugging
            pass

    def extract_comments(self, comment_element, current_depth=0):
        comments_data = []

        try:
            comments = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, f'shreddit-comment[depth="{current_depth}"]'))
            )

            for comment in comments:
                try:
                    author = comment.get_attribute("author")
                    score = comment.get_attribute("score")
                    content = comment.find_element(By.CSS_SELECTOR, 'div[id$="-post-rtjson-content"]').text

                    comment_data = {
                        "author": author,
                        "score": score,
                        "content": content,
                        "replies": []
                    }

                    next_depth = current_depth + 1
                    next_comments = comment.find_elements(By.CSS_SELECTOR, f'shreddit-comment[author][depth="{next_depth}"]')
                    if next_comments:
                        replies = self.extract_comments(comment, next_depth)
                        comment_data["replies"].extend(replies)

                    comments_data.append(comment_data)

                except StaleElementReferenceException:
                    # Stale element reference, retrying...
                    self.extract_comments(comment_element, current_depth)
                except Exception as e:
                    # print(f"Error extracting comment: {str(e)}") -------> For Debugging
                    pass

        except Exception as e:
            # print(f"Error extracting comments at depth {current_depth}: {str(e)}") -------> For Debugging
            pass

        return comments_data
       

    def extract_post_info(self):
        try:
            post_element = self.driver.find_element(By.CSS_SELECTOR, 'shreddit-post')

            post_title = post_element.get_attribute("post-title")
            author = post_element.get_attribute("author")

            post_id = post_element.get_attribute("id").split('-')[0][3:]
            post_score = post_element.get_attribute("score")

            flair_text = ""
            try:
                flair_element = post_element.find_element(By.CSS_SELECTOR, 'div.flair-content')
                flair_text = flair_element.text
            except Exception as e:
                # print(f"Flair element not found or incomplete: {str(e)}") -------> For Debugging
                pass             
            
            post_time = ""
            try:
                time_element = post_element.find_element(By.CSS_SELECTOR, 'time')
                post_time = time_element.get_attribute("title")
            except Exception as e:
                # print(f"Time element not found or incomplete: {str(e)}") -------> For Debugging
                 pass

            return post_title, author, post_id, post_score, post_time, flair_text
        
        except Exception as e:
            # print(f"Error extracting post information: {str(e)}") -------> For Debugging
            return None, None, None, None, None, None

    def scrape_post(self,driver):
        
        try:
            comments_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[id^="comment-tree-content-anchor"]'))
            )

            self.expand_comment_thread()

            post_title, post_author, post_id, post_score, post_time, flair_text = self.extract_post_info()

            if post_title and post_author and post_id: # The three are mandatory
                root_element = driver.find_element(By.CSS_SELECTOR, '[id^="comment-tree-content-anchor"]')
                comments_data = self.extract_comments(root_element, 0)

                data = {
                    "post_author": post_author,
                    "post_id": post_id,
                    "post_score": post_score,
                    "post_time": post_time,
                    "flair_text": flair_text,
                    "post_title": post_title,
                    "comments": comments_data
                }

                return data

            else:
                # print("Failed to extract post id, title and author.")   -------> For Debugging          
                return None

        except Exception as e:
            # print(f"Error: {str(e)}")  -------> For Debugging     
            return None

