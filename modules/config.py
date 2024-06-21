import os
from selenium.webdriver.chrome.options import Options
import modules.shared as shared
class Config:
    @staticmethod
    def get_chrome_options():
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
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

    @staticmethod
    def setup_json_file():
        if os.path.exists(shared.output_file_path):
            os.remove(shared.output_file_path)
