import threading
from flask import Flask, request, jsonify, render_template
from modules.config import Config
from modules.driver_utils import DriverUtils
from modules.scraper import SubredditScraper
import modules.shared as shared
import os

app = Flask(__name__)

# Initialize drivers and scraper globally
available_cpus = os.cpu_count()
if available_cpus is None or available_cpus < 1:
    available_cpus = 1

if shared.threads_number > available_cpus:
    if available_cpus > 1:
        shared.threads_number = available_cpus - 1
    else:
        shared.threads_number = 1


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    data = request.json
    subreddit = data.get('subreddit')
    max_posts = int(data.get('max_posts'))

    shared.processed_posts_count = 0  # Reset the processed posts count
    shared.max_post_number = max_posts  # Update the max_post_number
    shared.scroll_position = 0
    shared.threads = []

    shared.drivers = [DriverUtils.init_driver() for _ in range(shared.threads_number)]
    scraper = SubredditScraper(shared.drivers, shared.threads_number)

    Config.setup_json_file()
    scraper.update_scraper(subreddit, max_posts)
    scraper.scrape_subreddit()

    # scraper_thread = threading.Thread(target=scraper.scrape_subreddit)
    # scraper_thread.start()
    return jsonify({'message': 'Scraping started'}), 200

@app.route('/progress')
def progress():
    return jsonify({
        'processed_posts': shared.processed_posts_count,
        'max_posts': shared.max_post_number
    })

@app.route('/reset', methods=['POST'])
def reset():
    shared.processed_posts_count = 0
    shared.max_post_number = 0
    return jsonify({'message': 'Reset complete'}), 200


if __name__ == "__main__":
    app.run(debug=False)
