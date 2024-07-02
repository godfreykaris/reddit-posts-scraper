import os
import sys
import signal
import logging
import argparse
import requests
from flask import Flask, render_template, jsonify, request, send_from_directory
from modules.driver_utils import DriverUtils
from modules.threading_utils import ThreadManager
import modules.shared as shared
from modules.posts_processing import PostProcessor
import time
import threading

app = Flask(__name__)

# Configure logging to suppress specific messages
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Define the directory where scraped posts will be stored
DOWNLOAD_DIRECTORY = os.path.join(os.getcwd(), 'downloads')

exit_flag = threading.Event()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrape posts from a subreddit.")
    parser.add_argument("-s", "--subreddit", required=True, help="Name of the subreddit to scrape")
    parser.add_argument("-l", "--limit", type=int, help="Limit on the number of posts to scrape (default is infinite)")
    parser.add_argument("-c", "--categories", nargs='*', default=["hot", "new", "top"], help="Categories to scrape (default is 'hot', 'new', 'top')")
    parser.add_argument("-o", "--output", help="Output file path for the scraped posts (default is 'scraped_posts.json' in the current directory)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode to print processing details")
    parser.add_argument("-f", "--format", choices=['json', 'yaml', 'xml'], default='json', help="Output format for the scraped posts (default is 'json')")

    return parser.parse_args()

def initialize_shared_variables(output_path, format_type):
    shared.threads = {}
    shared.drivers = {}
    shared.processing_done = False
    shared.processing = True
    shared.processed_posts_count = 0

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

    shared.original_filepath_path = shared.output_file_path

    ThreadManager.remove_existing_output_file(shared.output_file_path)
    ThreadManager.recreate_directory(shared.output_file_path)

def create_threads(subreddit, limit, categories, verbose):
    if 'all' in categories:
        categories = ['hot', 'new', 'top']

    if len(categories) > 1:
        shared.maximum_workers = 2
    elif shared.limit < 500 and len(categories) == 1:
        shared.maximum_workers = 5

    for category in categories:
        if category not in ['hot', 'new', 'top']:
            print(f"Invalid category '{category}'. Skipping category.")
            continue

        manager = ThreadManager(subreddit, category, limit, verbose, shared.output_file_path)
        thread = manager.start_thread()
        shared.threads[category] = thread

def wait_for_threads_to_complete():
    while any(thread.is_alive() for thread in shared.threads.values()):
        if exit_flag.is_set():
            break
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scraping_route', methods=['POST'])
def start_scraping_route():
    data = request.json
    subreddit = data.get('subreddit', '')
    max_posts = int(data.get('max_posts')) or float('inf')
    category = data.get('category', '')
    file_name = data.get('file_name_input', '')
    file_type = data.get('file_type_input', '')

    shared.processing_done = False
    shared.processing = True
    
    output_path = os.path.join(DOWNLOAD_DIRECTORY, f"{file_name}.{file_type}")

    try:
        requests.get('https://www.google.com', timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        message = 'Unable to connect to the internet. Please check your connection.'
        return jsonify({'message': message}), 500

    DriverUtils.close_existing_chrome_instances()

    initialize_shared_variables(output_path, file_type)

    categories = [category]

    create_threads(subreddit, max_posts, categories, verbose=True)
    wait_for_threads_to_complete()
    
    if shared.processed_posts_count > 0:
        PostProcessor.finalize_file()
    if not shared.processing_done:
        shared.processing_done = True

    DriverUtils.quit_all_drivers()
    DriverUtils.close_existing_chrome_instances()

    shared.processing = False

    return jsonify({'message': 'Scraping Done.'}), 200

def start_scraping(subreddit, limit=None, categories=["hot", "new", "top"], output_path=None, verbose=True, format_type='json'):
    try:
        requests.get('https://www.google.com', timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        return "\n⚠️  Unable to connect to the internet. Please check your internet connection and try again."
    
    DriverUtils.close_existing_chrome_instances()

    print("Working....")
    initialize_shared_variables(output_path, format_type)

    create_threads(subreddit, limit, categories, verbose)
    wait_for_threads_to_complete()

    if shared.processed_posts_count > 0:
        PostProcessor.finalize_file()
    if not shared.processing_done:
        shared.processing_done = True
    
    DriverUtils.quit_all_drivers()
    DriverUtils.close_existing_chrome_instances()

    shared.processing = False

    if shared.processed_posts_count == 0:
        return "\n⚠️  No posts loaded. Please confirm the subreddit name and check the internet connection and try again."
    else:
        return f"\n✅ Output file: {shared.output_file_path}"
    
@app.route('/progress')
def progress():
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
    filename = os.path.basename(shared.output_file_path)
    return send_from_directory(os.path.dirname(shared.output_file_path), filename, as_attachment=True)

def finalize_and_exit(signum, frame):
    print("Quitting...")
    exit_flag.set()
    shared.processing_done = True
    if shared.processed_posts_count > 0:
        PostProcessor.finalize_file()
    DriverUtils.close_existing_chrome_instances()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, finalize_and_exit)

    if len(sys.argv) > 1:
        try:
            args = parse_arguments()
            start_scraping(args.subreddit, limit=args.limit, categories=args.categories, output_path=args.output, verbose=args.verbose, format_type=args.format)
        except Exception as e:
           sys.exit(0)
        if shared.processed_posts_count == 0:
            print("\n⚠️  No posts loaded. Please confirm the subreddit name and check the internet connection and try again.")
        else:
            print(f"\n✅ Output file(s): {shared.original_filepath_path}. Other generated files are in the same location.")
    else:
        app.run(debug=True)
