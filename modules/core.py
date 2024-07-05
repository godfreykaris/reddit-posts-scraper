from random import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

import modules.shared as shared

class RedditScraper:
    def __init__(self, driver):
        self.driver = driver
    
    def clean_content(self, value):
        if value is None:
            return ""

        if shared.format_type == 'json':
            lines = [line.strip() for line in value.splitlines()]
            clean_lines = [line for line in lines if line]
            return ' '.join(clean_lines)
        elif shared.format_type == 'xml':
            # Replace characters not allowed in XML with XML entities
            value = value.replace('&', '&amp;')  # Replace '&' with '&amp;'
            value = value.replace('<', '&lt;')   # Replace '<' with '&lt;'
            value = value.replace('>', '&gt;')   # Replace '>' with '&gt;'
            value = value.replace('"', '&quot;')  # Replace '"' with '&quot;'
            value = value.replace("'", '&apos;')  # Replace "'" with '&apos;'

            # Remove any non-printable characters
            value = ''.join(ch for ch in value if ch.isprintable())

            return value.strip()  # Strip leading/trailing whitespace
        else:
            return value.strip() 

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
            # Find comments within the current element at the specified depth
            comments = comment_element.find_elements(By.CSS_SELECTOR, f'shreddit-comment[depth="{current_depth}"]')

            for comment in comments:
                try:
                    author = comment.get_attribute("author")
                    score = comment.get_attribute("score")
                    content = comment.find_element(By.CSS_SELECTOR, 'div[id$="-post-rtjson-content"]').text
                    content = self.clean_content(content)
                    comment_data = {
                        "author": author,
                        "score": score,
                        "content": content
                    }

                    next_depth = current_depth + 1
                    next_comments = comment.find_elements(By.CSS_SELECTOR, f'shreddit-comment[author][depth="{next_depth}"]')
                    if next_comments:
                        replies = self.extract_comments(comment, next_depth)
                        if replies:  # Only include replies if they are not empty
                            comment_data["replies"] = replies
                        
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
            
            post_content = ""
            
            try:
                content_element = post_element.find_element(By.CSS_SELECTOR, 'div[id$="-post-rtjson-content"]')
                post_content = content_element.text
            except Exception as e:
                pass
        
            media_urls = set()

            def extract_media_urls(container, media_urls):
                # Find all image elements within the container
                media_images = container.find_elements(By.CSS_SELECTOR, 'img')
                media_urls.update(img.get_attribute("src") for img in media_images)
            
                # Find all video elements within the container
                media_videos = container.find_elements(By.CSS_SELECTOR, 'video source')
                media_urls.update(video.get_attribute("src") for video in media_videos)
            
                # Find all iframe elements within the container
                media_iframes = container.find_elements(By.CSS_SELECTOR, 'iframe')
                media_urls.update(iframe.get_attribute("src") for iframe in media_iframes)
            
                # Find all anchor elements within the container
                content_links = container.find_elements(By.CSS_SELECTOR, 'a')
                media_urls.update(link.get_attribute("href") for link in content_links)

                # Find all shredder-embed elements within the container
                embed_elements = container.find_elements(By.CSS_SELECTOR, 'shreddit-embed')
                for embed in embed_elements:
                    embed_html = embed.get_attribute("html")
                    if 'src="' in embed_html:
                        embed_url = embed_html.split('src="')[1].split('"')[0]
                        media_urls.add(embed_url)
                            
            # Retrieve media URLs (images, videos, iframes) from media container
            try:
                media_container = post_element.find_element(By.CSS_SELECTOR, 'div[slot="post-media-container"]')
                extract_media_urls(media_container, media_urls)
            except Exception as e:
                pass
            
            # Retrieve media URLs (images, videos, iframes) from content element
            try:
                extract_media_urls(content_element, media_urls)
            except Exception as e:
                pass

            return post_title, author, post_id, post_score, post_time, flair_text, post_content, list(media_urls)
        
        except Exception as e:
            # print(f"Error extracting post information: {str(e)}") -------> For Debugging
            return None, None, None, None, None, None, None, None



    def scrape_post(self,driver):
        
        try:
            comments_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[id^="comment-tree-content-anchor"]'))
            )

            self.expand_comment_thread()

            post_title, post_author, post_id, post_score, post_time, flair_text, post_content, media_urls = self.extract_post_info()

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
                    "media": media_urls,
                    "post_content":post_content,
                    "comments": comments_data
                }

                return data

            else:
                # print("Failed to extract post id, title and author.")   -------> For Debugging          
                return None

        except Exception as e:
            # print(f"Error: {str(e)}")  -------> For Debugging     
            return None

