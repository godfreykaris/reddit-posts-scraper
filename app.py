import threading
import argparse
import os

import requests

import modules.shared as shared
from modules.driver_utils import DriverUtils
from modules.threading_utils import ThreadManager, ensure_output_file_exists

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
    - args (Namespace): Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Scrape posts from a subreddit.")
    parser.add_argument("-s", "--subreddit", required=True, help="Name of the subreddit to scrape")
    parser.add_argument("-l", "--limit", type=int, help="Limit on the number of posts to scrape (default is infinite)")
    parser.add_argument("-c", "--categories", nargs='*', default=["hot", "new", "top"], help="Categories to scrape (default is 'hot', 'new', 'top')")
    parser.add_argument("-o", "--output", help="Output file path for the scraped posts (default is 'scraped_posts.json' in the current directory)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode to print processing details")
    parser.add_argument("-f", "--format", choices=['json', 'yaml', 'xml'], default='json', help="Output format for the scraped posts (default is 'json')")

    return parser.parse_args()

def initialize_shared_variables(output_path, format_type):
    """
    Initialize shared variables for the scraping process.

    Args:
    - output_path (str): Output file path for the scraped posts.
    - format_type (str): Desired output format ('json', 'yaml', 'xml').
    """
    # Reset global variables
    shared.threads = {}
    shared.processing_completed = False

    # Set the output file path based on user input or default
    if output_path:
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
            shared.output_file_path = f"{os.path.splitext(output_path)[0]}.{format_type}"
    else:
        shared.output_file_path = os.path.join(os.getcwd(), f"reddit-posts\\scraped_posts.{format_type}")

    ensure_output_file_exists(shared.output_file_path)

def create_threads(subreddit, limit, categories, verbose):
    """
    Create and start threads for scraping each category.

    Args:
    - subreddit (str): Name of the subreddit to scrape.
    - limit (int): Limit on the number of posts to scrape.
    - categories (list): List of categories to scrape ('hot', 'new', 'top', 'all').
    - verbose (bool): Enable verbose mode to print processing details.
    """

    if 'all' in categories:
        categories = ['hot', 'new', 'top']

    for category in categories:
        if category not in ['hot', 'new', 'top']:
            print(f"Invalid category '{category}'. Skipping category.")
            continue

        manager = ThreadManager(subreddit, category, limit, verbose, shared.output_file_path)
        thread = manager.start_thread()
        shared.threads[category] = thread

def wait_for_threads_to_complete():
    """
    Wait for all threads to complete.
    """
    for category, thread in shared.threads.items():
        thread.join()

    shared.processing_completed = True

def start_scraping(subreddit, limit=None, categories=["hot", "new", "top"], output_path=None, verbose=False, format_type='json'):
    """
    Start scraping posts from the specified subreddit.

    Args:
    - subreddit (str): Name of the subreddit to scrape.
    - limit (int): Limit on the number of posts to scrape (default is infinite).
    - categories (list): List of categories to scrape ('hot', 'new', 'top', or 'all'; default is  all i.e. ['hot', 'new', 'top']).
    - output_path (str): Output file path for the scraped posts.
    - verbose (bool): Enable verbose mode to print processing details.
    - format_type (str): Desired output format ('json', 'yaml', 'xml'; default is 'json').
    """
    
    try:
        # Check internet connection
        requests.get('https://www.google.com', timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        print("\n⚠️  Unable to connect to the internet. Please check your internet connection and try again.")
        return
    
    # Close any existing chrome instances
    DriverUtils.close_existing_chrome_instances()

    print("Working....")
    initialize_shared_variables(output_path, format_type)
    create_threads(subreddit, limit, categories, verbose)
    wait_for_threads_to_complete()

    # Check if any posts were processed
    if shared.processed_posts_count == 0:
        print("\n⚠️  No posts loaded. Please confirm the subreddit name and check the internet connection and try again.")
    else:
        print(f"\n✅ Output file: {shared.output_file_path}")

if __name__ == "__main__":
    args = parse_arguments()
    start_scraping(args.subreddit, limit=args.limit, categories=args.categories, output_path=args.output, verbose=args.verbose, format_type=args.format)

