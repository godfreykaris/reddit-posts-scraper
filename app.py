import threading
import argparse
import os

import xml.etree.ElementTree as ET
from modules.config import Config
from modules.driver_utils import DriverUtils
from modules.posts_processing import PostProcessor
from modules.scraper import SubredditScraper
import modules.shared as shared


def initialize_driver(category):
    """
    Initialize the WebDriver if it's not already initialized for a specific category.

    Args:
    - category (str): Category for which to initialize the driver.
    """
    if shared.drivers.get(category) is None:
        shared.drivers[category] = DriverUtils.init_driver()

def ensure_output_file_exists(output_path):
    """
    Ensure that the output file exists by creating it if it doesn't already exist.

    Args:
    - output_path (str): Path to the output file.
    """
    if os.path.exists(output_path):
        os.remove(output_path)  # Remove the existing file if it exists

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create an empty file
    with open(output_path, 'w'):
        pass

def scrape_category(subreddit, category, limit, verbose, output_path):
    """
    Scrape posts from a specific category of subreddit.

    Args:
    - subreddit (str): Name of the subreddit to scrape.
    - category (str): Category to scrape ('hot', 'new', 'top').
    - limit (int): Limit on the number of posts to scrape.
    - verbose (bool): Enable verbose mode to print processing details.
    - format_type (str): Desired output format ('json', 'yaml', 'xml').
    - output_path (str): Output file path for the scraped posts.
    """
    print(f"Thread {threading.get_ident()}: Scraping {category} category....")
    initialize_driver(category)

    # Set up shared variables
    shared.processed_posts_count = 0
    shared.limit = limit if limit is not None else float('inf')
    shared.scroll_position = 0
    shared.verbose = verbose
    shared.output_file_path = output_path

    shared.scraper = SubredditScraper(shared.drivers[category])
    Config.setup_output_file()

    shared.scraper.update_scraper(shared.limit)

    base_url = f"https://www.reddit.com/r/{subreddit}/"
    if category == "hot":
        shared.reddit_url = base_url + "hot/"
    elif category == "new":
        shared.reddit_url = base_url + "new/"
    elif category == "top":
        shared.reddit_url = base_url + "top/?t=all"
    else:
        print(f"Thread {threading.get_ident()}: Invalid category {category}. Skipping category.\n")
        return
    
    shared.scraper.scrape_subreddit()

    # Finalize the output file
    with shared.lock:
        PostProcessor.finalize_file()

def start_scraping(subreddit, limit=None, categories=["all"], output_path=None, verbose=False, format_type='json'):
    """
    Start scraping posts from the specified subreddit.

    Args:
    - subreddit (str): Name of the subreddit to scrape.
    - limit (int): Limit on the number of posts to scrape (default is infinite).
    - categories (list): List of categories to scrape ('hot', 'new', 'top', or 'all'; default is ['all']).
    - output_path (str): Output file path for the scraped posts.
    - verbose (bool): Enable verbose mode to print processing details.
    - format_type (str): Desired output format ('json', 'yaml', 'xml'; default is 'json').
    """

    print("Working....")

    # Reset global variables
    shared.threads = {}
    shared.processing_completed = False

    # Set the output file path based on user input or default
    if output_path:
        # Check if the provided output_path ends with .json, .yaml, or .xml
        if output_path.endswith('.json'):
            shared.output_file_path = output_path
            shared.format_type = 'json'
        elif output_path.endswith('.yaml'):
            shared.output_file_path = output_path
            shared.format_type = 'yaml'
        elif output_path.endswith('.xml'):
            shared.output_file_path = output_path
            shared.format_type = 'xml'
        else:
            # If no valid extension is found, use the base name and add the format_type extension
            shared.output_file_path = f"{os.path.splitext(output_path)[0]}.{shared.format_type}"
    else:
        # If no output_path is provided, use the default path with format_type
        shared.output_file_path = os.path.join(os.getcwd(), f"reddit-posts\\scraped_posts.{shared.format_type}")

    # Ensure the output file exists
    ensure_output_file_exists(shared.output_file_path)

    # Create threads for each category
    for category in categories:
        if category not in ['hot', 'new', 'top', 'all']:
            print(f"Invalid category '{category}'. Skipping category.")
            continue

        thread = threading.Thread(target=scrape_category, args=(subreddit, category, limit, verbose, shared.output_file_path))
        shared.threads[category] = thread
        thread.start()

    # Wait for all threads to complete
    for category, thread in shared.threads.items():
        thread.join()

    shared.processing_completed = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape posts from a subreddit.")
    parser.add_argument("-s", "--subreddit", required=True, help="Name of the subreddit to scrape")
    parser.add_argument("-l", "--limit", type=int, help="Limit on the number of posts to scrape (default is infinite)")
    parser.add_argument("-c", "--categories", nargs='*', default=["hot", "new", "top"], help="Categories to scrape (default is 'hot', 'new', 'top')")
    parser.add_argument("-o", "--output", help="Output file path for the scraped posts (default is 'scraped_posts.json' in the current directory)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode to print processing details")
    parser.add_argument("-f", "--format", choices=['json', 'yaml', 'xml'], default='json', help="Output format for the scraped posts (default is 'json')")

    args = parser.parse_args()

    start_scraping(args.subreddit, limit=args.limit, categories=args.categories, output_path=args.output, verbose=args.verbose, format_type=args.format)

    if shared.processed_posts_count == 0:
        print("\nNo posts loaded. Please confirm the subreddit name and try again.")
    else:
        print(f"\nOutput file: {shared.output_file_path}")
