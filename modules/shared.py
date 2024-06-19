import threading

# Shared scroll position and mutex for synchronization
scroll_position = 0
scroll_mutex = threading.Lock()

# Event to signal termination
terminate_event = threading.Event()

# Global variable to count processed posts
processed_posts_count = 0
processed_posts_lock = threading.Lock()

# Set threads_number to 1
threads_number = 1

# Max post number
max_post_number = 0

processing_started = False
processing_completed = False