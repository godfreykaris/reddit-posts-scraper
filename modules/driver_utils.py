from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from modules.config import Config
import time

class DriverUtils:
    @staticmethod
    def init_driver():
        driver_path = "chromedriver/chromedriver.exe"  # Adjust path as necessary
        service = Service(driver_path)
        
        driver = webdriver.Chrome(service=service, options=Config.get_chrome_options())
        driver.maximize_window()  # Maximize the window
        
        return driver

    @staticmethod
    def access_subreddit(subreddit, driver):
        url = f"https://www.reddit.com/r/{subreddit}/"
        driver.get(url)
        time.sleep(5)  

    @staticmethod
    def scroll_to_bottom(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    @staticmethod
    def get_document_element(driver):
        return driver.execute_script("return document.documentElement.outerHTML;")

    @staticmethod
    def new_posts_loaded(old_html, new_html):
        return old_html != new_html
