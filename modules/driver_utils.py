import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from modules.config import Config

class DriverUtils:
    @staticmethod
    def init_driver():
        return webdriver.Chrome(service=Service(Config.driver_path), options=Config.get_chrome_options())

    @staticmethod
    def is_driver_alive(driver):
        try:
            driver.current_url
            return True
        except WebDriverException:
            return False

    @staticmethod
    def access_subreddit(subreddit, driver):
        url = f'https://www.reddit.com/r/{subreddit}/'
        driver.get(url)
        time.sleep(3)

    @staticmethod
    def get_initial_scroll_position(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        return driver.execute_script("return window.pageYOffset;")
