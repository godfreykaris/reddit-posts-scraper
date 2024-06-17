import threading

# Shared scroll position and mutex for synchronization
scroll_position = 0
scroll_mutex = threading.Lock()

# Event to signal termination
terminate_event = threading.Event()

# Global variable to count processed posts
processed_posts_count = 0
processed_posts_lock = threading.Lock()

# Lock for recording posts
recording_post_lock = threading.Lock()

# Threads and chrome drivers
threads = []
threads_number = 3
drivers = None

# Max post number
max_post_number = 0