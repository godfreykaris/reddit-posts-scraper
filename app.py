import sys
import threading
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
from modules.config import Config
from modules.driver_utils import DriverUtils
from modules.posts_processing import PostProcessor
from modules.scraper import SubredditScraper
import modules.shared as shared
import os

app = Flask(__name__)

# Global variables for the driver and scraper
shared.driver = None
shared.scraper = None

shared.output_file_path = os.path.join(os.getcwd(), "scraped_posts.json")

# Initialize the global driver
def initialize_driver():
    if shared.driver is None:
        shared.driver = DriverUtils.init_driver()

# Initialize driver when the app starts
initialize_driver()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    data = request.json
    subreddit = data.get('subreddit')
    max_posts = int(data.get('max_posts'))

    category = data.get('category', 'hot')  # Default to 'hot' if no category is provided
    categories_to_scrape = []
    if category == "all":
        categories_to_scrape = ["hot", "new", "top"]
    else:
        categories_to_scrape = [category]

    shared.processed_posts_count = 0  # Reset the processed posts count
    shared.max_post_number = max_posts  # Update the max_post_number
    shared.scroll_position = 0
    shared.threads = []

    shared.processing_started = False
    shared.processing_completed = False

    # Reinitialize the driver if it's not initialized or has been closed
    initialize_driver()

    shared.scraper = SubredditScraper(shared.driver)
    Config.setup_json_file()
    shared.scraper.update_scraper(max_posts)

    for cat in categories_to_scrape:
        print(cat)
        base_url = f"https://www.reddit.com/r/{subreddit}/"
        if cat == "hot":
            shared.reddit_url = base_url + "hot/"
        elif cat == "new":
            shared.reddit_url = base_url + "new/"
        elif cat == "top":
            shared.reddit_url = base_url + "top/?t=all"
        else:
            print("Invalid category. Skipping category.")
            continue

        shared.scraper.scrape_subreddit()

        if cat == categories_to_scrape[-1] or shared.processed_posts_count >= shared.max_post_number:
            PostProcessor.finalize_json_file()
            shared.processing_completed = True
            break

    return jsonify({'message': 'Scraping started'}), 200

@app.route('/progress')
def progress():
    return jsonify({
        'processed_posts': shared.processed_posts_count,
        'max_posts': shared.max_post_number,
        'processing_done': shared.processing_completed,
        'processing_started': shared.processing_started
    })

@app.route('/reset', methods=['POST'])
def reset():
    shared.processed_posts_count = 0
    shared.max_post_number = 0
    return jsonify({'message': 'Reset complete'}), 200

@app.route('/download', methods=['GET'])
def download_file():
    directory = os.path.dirname(shared.output_file_path)
    filename = os.path.basename(shared.output_file_path)
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False)
