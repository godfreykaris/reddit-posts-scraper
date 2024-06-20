import threading
from flask import Flask, request, jsonify, render_template, redirect, url_for
from modules.config import Config
from modules.driver_utils import DriverUtils
from modules.scraper import SubredditScraper
import modules.shared as shared
import os

app = Flask(__name__)

# Global variables for the driver and scraper
shared.driver = None
shared.scraper = None

# Initialize the global driver
def initialize_driver():
    if shared.driver is None:
        shared.driver = DriverUtils.init_driver()

# Initialize driver when the app starts
initialize_driver()

# Route to quit the application and close the driver
@app.route('/quit')
def quit_app():
    global shared
    if shared.driver:
        shared.driver.quit()
        shared.driver = None
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    data = request.json
    subreddit = data.get('subreddit')
    max_posts = int(data.get('max_posts'))

    category = data.get('category', 'hot')  # Default to 'hot' if no category is provided

    # Construct the URL based on the selected category
    base_url = f"https://www.reddit.com/r/{subreddit}/"
    if category == "hot":
        shared.reddit_url = base_url + "hot/"
    elif category == "new":
        shared.reddit_url = base_url + "new/"
    elif category == "top":
        shared.reddit_url = base_url + "top/?t=all"
    else:
        print("Invalid category. Defaulting to Hot.")
        shared.reddit_url = base_url + "hot/"

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
    shared.scraper.scrape_subreddit()

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

if __name__ == "__main__":
    app.run(debug=False)
