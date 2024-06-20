from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service('chromedriver/chromedriver.exe'))

# Prompt the user for the post category
category = input("Enter the post category (Hot, New, Top): ").strip().lower()

# Construct the URL based on user input
base_url = "https://www.reddit.com/r/Python/"
if category == "hot":
    url = base_url + "hot/"
elif category == "new":
    url = base_url + "new/"
elif category == "top":
    url = base_url + "top/?t=all"
else:
    print("Invalid category. Defaulting to Hot.")
    url = base_url + "hot/"

# Open the Reddit URL
driver.get(url)

# Function to scroll to the bottom of the page
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for content to load

# Function to retrieve the document element
def get_document_element(driver):
    return driver.execute_script("return document.documentElement.outerHTML;")

# Function to check if new posts were loaded
def new_posts_loaded(old_html, new_html):
    return old_html != new_html

# Function to process posts
def process_posts(driver, min_posts=3000):
    post_count = 0
    previous_html = None

    # Open the JSON file in write mode to initialize it
    with open("reddit_posts.json", "w", encoding="utf-8") as f:
        f.write("[\n")

    while post_count < min_posts:
        scroll_to_bottom(driver)

        # Retrieve and process page content
        new_html = get_document_element(driver)
        
        # Check if new posts were loaded
        if not new_posts_loaded(previous_html, new_html):
            print("No new posts loaded. Terminating.")
            break
        
        previous_html = new_html
        
        soup = BeautifulSoup(new_html, 'html.parser')
        posts = soup.find_all('article')

        new_posts = []
        for post in posts:
            try:
                title_element = post.find('a', {'data-click-id': 'body'})
                title = title_element.text if title_element else "No title"

                content_element = post.find('div', id=lambda x: x and x.endswith('-post-rtjson-content'))
                content = content_element.text.strip() if content_element else "No content"

                post_data = {
                    "title": title,
                    "content": content
                }

                new_posts.append(post_data)
                post_count += 1

                if post_count >= min_posts:
                    break

            except Exception as e:
                print(f"Error processing post: {e}")

        # Append new posts to the JSON file
        with open("reddit_posts.json", "a", encoding="utf-8") as f:
            for post_data in new_posts:
                json.dump(post_data, f, ensure_ascii=False, indent=4)
                f.write(",\n")

    # Close the JSON array in the file
    with open("reddit_posts.json", "a", encoding="utf-8") as f:
        f.seek(f.tell() - 2, 0)  # Remove the last comma and newline
        f.write("\n]")

    return post_count

# Measure time taken for processing posts
start_time = time.time()

# Scroll to the bottom and retrieve content until minimum posts are collected
min_posts = 3000

posts_collected = process_posts(driver, min_posts=min_posts)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Collected {posts_collected} posts in {elapsed_time:.2f} seconds.")

# Close the browser
driver.quit()
