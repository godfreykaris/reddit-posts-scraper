import threading

# Global variables for the drivers and scraper
drivers = {}  # Dictionary to store drivers for each category
threads = {}  # Dictionary to store threads for each category
lock = threading.Lock()  # Lock to synchronize access to shared variables

# Thread color mapping for each thread to print its output in a drifferent color
thread_colors = {}

# Worker threads limit
maximum_workers = 8

# Global variable to count processed posts
processed_posts_count = 0

# Maximum post number
limit = 0

# Print progress on the console
verbose = False

# Output file format ['json', 'yaml']
format_type = "json"

# Reddit Posts URL
reddit_url = ''

# Output filepath
output_file_path = "" # This can change based on the file exceeding size limit
original_filepath_path = ""

# Used for communication with the frontend incase the user decides to use the flask app
processing = False
processing_done = False