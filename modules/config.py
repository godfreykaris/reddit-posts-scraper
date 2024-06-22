import os
from selenium.webdriver.chrome.options import Options
import modules.shared as shared

class Config:
    @staticmethod
    def get_chrome_options():
        """
        Get Chrome options for configuring WebDriver.
        
        Returns:
        - selenium.webdriver.chrome.options.Options: Chrome Options instance with configured options.
        """
        chrome_options = Options()  # Initialize Chrome Options
        
        # Add various arguments to Chrome Options
        chrome_options.add_argument("--headless=new")  # Set headless mode
        chrome_options.add_argument("disable-infobars")  # Disable infobars
        chrome_options.add_argument("--disable-extensions")  # Disable extensions
        chrome_options.add_argument("--disable-dev-shm-usage")  # Disable dev-shm-usage
        chrome_options.add_argument("user-agent=Chrome/126.0.0.0")  # Set user agent
        chrome_options.add_argument('--ignore-ssl-errors=yes')  # Ignore SSL errors
        chrome_options.add_argument('--ignore-certificate-errors')  # Ignore certificate errors
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')

        # Set log level to only log errors
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Exclude logging
        
        return chrome_options  # Return configured Chrome Options instance

    @staticmethod
    def setup_output_file():
        """
        Setup output file by removing it if it already exists.

        This method checks if the output_file_path exists in the shared module,
        and removes it if it does, ensuring a fresh start for output file setup.

        """
        output_file_path = shared.output_file_path + f'.{shared.format_type}'
        
        if os.path.exists(output_file_path):
            os.remove(output_file_path)  # Remove the existing output file if it exists
