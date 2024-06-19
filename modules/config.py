import os
from selenium.webdriver.chrome.options import Options

class Config:
    @staticmethod
    def get_chrome_options():
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")
        chrome_options.page_load_strategy = 'none'
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Chrome/126.0.0.0")
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')

        # Only log errors
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        return chrome_options

    driver_path = "chromedriver/chromedriver.exe"
    json_filename = "processed_posts.json"

    @staticmethod
    def setup_json_file():
        if os.path.exists(Config.json_filename):
            os.remove(Config.json_filename)
