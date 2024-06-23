import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from modules.config import Config
import modules.shared as shared
import time
import psutil

class DriverUtils:
    @staticmethod
    def close_existing_chrome_instances():
        """
        Close existing Chrome instances by terminating their processes.
        """
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'chrome' or proc.info['name'] == 'chrome.exe':
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    proc.kill()
    @staticmethod
    def initialize_driver(category):
        """
        Initialize the WebDriver if it's not already initialized for a specific category.

        Args:
        - category (str): Category for which to initialize the driver.
        """
        if shared.drivers.get(category) is None:
            shared.drivers[category] = DriverUtils.create_driver()
    @staticmethod
    def create_driver():
        """
        Create and return a Chrome WebDriver instance.

        Returns:
        - webdriver.Chrome: Initialized Chrome WebDriver instance.
        """
        driver_path = "chromedriver/chromedriver.exe"  # Adjust path as necessary
        service = Service(driver_path)  # Create a WebDriver service
        
        # Initialize Chrome WebDriver with service and options
        driver = webdriver.Chrome(service=service, options=Config.get_chrome_options())
        driver.maximize_window()  # Maximize the window
        
        return driver  # Return the initialized WebDriver instance

    @staticmethod
    def access_subreddit(driver):
        """
        Access the subreddit page using the provided WebDriver instance.

        Args:
        - driver (webdriver.Chrome): Chrome WebDriver instance.
        """
        driver.get(shared.reddit_url)  # Load the URL specified in shared.reddit_url
        time.sleep(5)  # Wait for 5 seconds to allow the page to load

    @staticmethod
    def scroll_to_bottom(driver):
        """
        Scroll to the bottom of the current page using the provided WebDriver instance.

        Args:
        - driver (webdriver.Chrome): Chrome WebDriver instance.
        """
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Execute JavaScript to scroll to the bottom
        time.sleep(random.uniform(3.0, 4.5))  # Random sleep between 3.0 and 4.5 seconds

    @staticmethod
    def get_document_element(driver):
        """
        Retrieve the HTML content of the entire document using the provided WebDriver instance.

        Args:
        - driver (webdriver.Chrome): Chrome WebDriver instance.

        Returns:
        - str: Outer HTML content of the document.
        """
        return driver.execute_script("return document.documentElement.outerHTML;")  # Execute JavaScript to return outer HTML content

    @staticmethod
    def new_posts_loaded(old_html, new_html):
        """
        Check if new posts have loaded by comparing old and new HTML content.

        Args:
        - old_html (str): Old HTML content.
        - new_html (str): New HTML content.

        Returns:
        - bool: True if new posts have loaded (content is different), False otherwise.
        """
        return old_html != new_html  # Compare old and new HTML content to determine if new posts have loaded
