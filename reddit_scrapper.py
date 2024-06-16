import threading
import time
import signal
import sys
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Chrome/126.0.0.0")

# Set up the Chrome driver path
driver_path = "chromedriver/chromedriver.exe"

# Shared scroll position and mutex for synchronization
scroll_position = 0
scroll_mutex = threading.Lock()

# Event to signal termination
terminate_event = threading.Event()

# Global variable to count processed articles
processed_articles_count = 0
processed_articles_lock = threading.Lock()

recording_artcle_lock = threading.Lock()

# JSON file to write processed data
json_filename = "processed_articles.json"

# Delete the file if it exists
if os.path.exists(json_filename):
    os.remove(json_filename)

threads = []
drivers = None


def write_article_to_json(json_filename, title, author, content):
    article = {
        'Title': title,
        'Author': author,
        'Content': content
    }

    mode = 'a' if os.path.exists(json_filename) else 'w'
    with open(json_filename, mode, encoding='utf-8') as json_file:
        if mode == 'a':
            json_file.write(',\n')  # Separate entries in the array with a comma and newline
        else:
            json_file.write('[\n')

        json.dump(article, json_file, ensure_ascii=False)


def finalize_json_file(json_filename):
    with open(json_filename, 'a', encoding='utf-8') as json_file:
        json_file.write('\n]')  # Close the JSON array with a closing square bracket


def init_driver():
    return webdriver.Chrome(service=Service(driver_path), options=chrome_options)


def access_subreddit(subreddit, driver):
    url = f'https://www.reddit.com/r/{subreddit}/'
    driver.get(url)
    time.sleep(3)


def get_initial_scroll_position(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    return driver.execute_script("return window.pageYOffset;")


def is_driver_alive(driver):
    try:
        driver.current_url
        return True
    except WebDriverException:
        return False


def extract_articles(driver):
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            articles = driver.find_elements(By.CSS_SELECTOR, "article[aria-label]")
            return articles
        except Exception as e:
            if not is_driver_alive(driver):
                print("Driver is no longer alive. Terminating function.")
                return None

            retry_count += 1
            if retry_count == max_retries:
                print(f"Failed after {max_retries} attempts due to: {e}")
                raise
            else:
                print(f"Retrying ({retry_count}/{max_retries}) after exception: {e}")
                time.sleep(2)  # Wait before retrying


def process_articles(articles, driver, max_article_number):
    global processed_articles_count

    for article in articles:
        try:
            title = article.find_element(By.CSS_SELECTOR, "a[href^='/r/']").text
            author = article.find_element(By.CSS_SELECTOR, "a[href^='/user/']").text[2:]

            # Extract article content
            content_element = article.find_element(By.CSS_SELECTOR, "div[id$='-post-rtjson-content']")
            if(content_element):
                article_content = content_element.text.strip()
            else:
                article_content = ""

            # Write article to JSON file
            with recording_artcle_lock:
                write_article_to_json(json_filename, title, author, article_content)

            # Increment processed articles count in a thread-safe manner
            with processed_articles_lock:
                processed_articles_count += 1

            # Check if we've reached the maximum set number
            if processed_articles_count >= max_article_number:
                print(f"Processed {processed_articles_count} articles. Terminating...")
                terminate_event.set()
                return

        except Exception as e:
            if not is_driver_alive(driver):
                print("Driver is no longer alive. Terminating function.")
                return None


def scroll_and_extract(subreddit, driver, driver_index, initial_scroll_position, max_article_number):
    global scroll_position
    global processed_articles_count

    if scroll_position == 0:
        scroll_position = initial_scroll_position

    if driver_index != 0:
        access_subreddit(subreddit, driver)
    
    print("Starting")

    while processed_articles_count < max_article_number and not terminate_event.is_set():
        with scroll_mutex:
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            scroll_position += initial_scroll_position


        time.sleep(2)
        articles = extract_articles(driver)
        # Release the lock and then process articles
        if articles is not None:
            process_articles(articles, driver, max_article_number)


def scrape_subreddit(subreddit, num_threads, max_articles):
    global threads
    global drivers
    global max_article_number

    max_article_number = max_articles

    drivers = [init_driver() for _ in range(num_threads)]  # Initialize one driver per thread

    # Access subreddit for all drivers
    access_subreddit(subreddit, drivers[0])

    time.sleep(3)
    initial_scroll_position = get_initial_scroll_position(drivers[0])

    while initial_scroll_position == 0:
        initial_scroll_position = get_initial_scroll_position(drivers[0])

    threads = []
    for idx in range(num_threads):
        thread = threading.Thread(target=scroll_and_extract, args=(subreddit, drivers[idx], idx, initial_scroll_position, max_article_number))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete or terminate on processing the specified number of articles
    for thread in threads:
        thread.join()

    # After all threads are done, quit all drivers
    for driver in drivers:
        driver.quit()

    # Print total processed articles count
    print(f"Total processed articles: {processed_articles_count}")


# Function to handle user input
def handle_user_input():
    while True:
        user_input = input("Enter subreddit name and maximum number of posts (e.g., Python 1000): ")
        inputs = user_input.split()
        if len(inputs) == 2:
            subreddit = inputs[0]
            try:
                max_posts = int(inputs[1])
                
                scrape_subreddit(subreddit, 6, max_posts)  # Adjust number of threads as needed
                finalize_json_file(json_filename)
                print(f"Scraping completed. Data saved in {json_filename}")
                break
            except ValueError:
                print("Invalid input for maximum number of posts. Please enter a valid integer.")
        else:
            print("Invalid input format. Please enter subreddit name and maximum number of posts.")


# Set up signal handler for Ctrl+C
def signal_handler(sig, frame):
    print("\nCtrl+C pressed. Cleaning up resources...")
    # Quit all drivers after threads are done
    for driver in drivers:
        driver.quit()
    sys.exit(0)


# Set up signal handler
signal.signal(signal.SIGINT, signal_handler)

# Usage example
if __name__ == "__main__":
    print("Welcome to Reddit Scraper!")
    handle_user_input()
