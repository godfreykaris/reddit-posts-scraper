import os
import sys
import argparse
import requests
from flask import Flask, render_template, jsonify, request, send_from_directory
from modules.driver_utils import DriverUtils
from modules.threading_utils import ThreadManager
import modules.shared as shared
from modules.posts_processing import PostProcessor

app = Flask(__name__)

# Define the directory where scraped posts will be stored
DOWNLOAD_DIRECTORY = os.path.join(os.getcwd(), 'downloads')

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
    shared.drivers = {}
    shared.processing_done = False
    shared.processing = True
    shared.processed_posts_count = 0

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
        shared.output_file_path = os.path.join(DOWNLOAD_DIRECTORY, f"scraped_posts.{format_type}")

    ThreadManager.remove_existing_output_file(shared.output_file_path)
    ThreadManager.recreate_directory(shared.output_file_path)

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


@app.route('/')
def index():
    """
    Render the index.html template.
    """
    return render_template('index.html')

@app.route('/start_scraping_route', methods=['POST'])
def start_scraping_route():
    """
    Endpoint to start scraping process.

    Expects form data with subreddit, max_posts, category, download_folder_input, file_name_input, and file_type_input.
    """
    data = request.json
    subreddit = data.get('subreddit', '')
    max_posts = float('inf')#int(data.get('max_posts', float('inf')))
    category = data.get('category', '')
    file_name = data.get('file_name_input', '')
    file_type = data.get('file_type_input', '')

    # Joining download_folder, file_name, and file_type into output_path
    output_path = os.path.join(DOWNLOAD_DIRECTORY, f"{file_name}.{file_type}")

    try:
        # Check internet connection before proceeding
        requests.get('https://www.google.com', timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        message = 'Unable to connect to the internet. Please check your connection.'
        return jsonify({'message': message}), 500

    # Close any existing chrome instances
    DriverUtils.close_existing_chrome_instances()

    # Initialize shared variables and setup output file
    initialize_shared_variables(output_path, file_type)

    category = [category]
    # Create threads for scraping
    create_threads(subreddit, max_posts, category, verbose=True)
    wait_for_threads_to_complete()

    shared.processing = False
    shared.processing_done = True

    DriverUtils.quit_all_drivers()

    return jsonify({'message': 'Scraping Done.'}), 200

def start_scraping(subreddit, limit=None, categories=["hot", "new", "top"], output_path=None, verbose=False, format_type='json'):
    """
    Start scraping posts from the specified subreddit.

    Args:
    - subreddit (str): Name of the subreddit to scrape.
    - limit (int): Limit on the number of posts to scrape (default is infinite).
    - categories (list): List of categories to scrape ('hot', 'new', 'top', or 'all'; default is all i.e. ['hot', 'new', 'top']).
    - output_path (str): Output file path for the scraped posts.
    - verbose (bool): Enable verbose mode to print processing details.
    - format_type (str): Desired output format ('json', 'yaml', 'xml'; default is 'json').
    """
    try:
        # Check internet connection
        requests.get('https://www.google.com', timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        return "\n⚠️  Unable to connect to the internet. Please check your internet connection and try again."
    
    # Close any existing chrome instances
    DriverUtils.close_existing_chrome_instances()

    print("Working....")
    initialize_shared_variables(output_path, format_type)
    create_threads(subreddit, limit, categories, verbose)
    wait_for_threads_to_complete()

    DriverUtils.quit_all_drivers()

    # Check if any posts were processed
    if shared.processed_posts_count == 0:
        return "\n⚠️  No posts loaded. Please confirm the subreddit name and check the internet connection and try again."
    else:
        return f"\n✅ Output file: {shared.output_file_path}"
    
@app.route('/progress')
def progress():
    """
    Endpoint to fetch scraping progress.
    """
    processed_posts = shared.processed_posts_count
    if shared.limit == float('inf'):
        max_posts = 'As many as available'
    else:
        max_posts = shared.limit
    processing_done = shared.processing_done

    return jsonify({
        'processed_posts': processed_posts,
        'max_posts': max_posts,
        'processing_done': processing_done,
        'processing': shared.processing
    })

@app.route('/download')
def download():
    """
    Endpoint to download scraped posts.
    """
    filename = os.path.basename(shared.output_file_path)
    return send_from_directory(os.path.dirname(shared.output_file_path), filename, as_attachment=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = parse_arguments()
        start_scraping(args.subreddit, limit=args.limit, categories=args.categories, output_path=args.output, verbose=args.verbose, format_type=args.format)

        if shared.processed_posts_count == 0:
            print("\n⚠️  No posts loaded. Please confirm the subreddit name and check the internet connection and try again.")
        else:
            print(f"\n✅ Output file: {shared.output_file_path}")
    else:
        # If no command-line arguments, run the Flask app
        app.run(debug=True)

