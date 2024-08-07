# Reddit Scraper

A web scraping application designed to extract posts from a specified subreddit. The application uses Selenium and BeautifulSoup to navigate and parse the content of Reddit posts, and saves the results to a JSON file.

## 1. Features

- **Scrapes Multiple Categories**: Allows scraping from multiple categories such as 'hot', 'new', 'top', or all categories combined.
- **Multi-threaded Scraping**: Utilizes threads for concurrent scraping when either multiple categories are selected or no specific category is specified, optimizing performance.
- **Output Formats**: Supports output formats including JSON, YAML and XML.
- **Dynamic Output File Naming**: Automatically names output files based on specified file path and optional format.
- **Progress Monitoring**: Provides real-time progress updates during the scraping process.
- **Error Handling**: Handles errors gracefully, skipping invalid categories and displaying relevant messages.
- **Customizable Limits**: Allows setting a limit on the number of posts to scrape.
- **Verbose Mode**: Enables verbose mode to print detailed processing information.


## 2. Technologies Used

- Python
- Selenium
- BeautifulSoup

## 3. Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.8 or later.
- You have `pip` installed.
- You have Google Chrome installed.
- You have downloaded the ChromeDriver that matches your Chrome version and placed it in a directory accessible to your PATH.
- You may need to enable Python in your system settings. If you're facing the "Manage App Execution Aliases" issue, follow these steps:
  - Go to your search bar and search for "Manage App Execution Aliases".
  - In the window that opens, turn off "App Installers" for Python.

## 4. Installing Python (If not found)

If you receive a "Python not found" error, you will need to install Python. Follow these steps:

1. Download the latest version of Python from the [official Python website](https://www.python.org/downloads/).
2. Run the installer and make sure to check the box that says "Add Python to PATH".
3. Follow the installation prompts.
4. Verify the installation by opening a command prompt and running:
   ```bash
   python --version
   ```
5. If the installation was successful, you should see the Python version number.

## 5 Setup

### 5.1 Increase Git Buffer Size:
Increase the buffer size to allow fetching of the ChromeDriver from the repository:
```sh
git config --global http.postBuffer 104857600
```

### 5.2 Clone the Repository

```sh
git clone https://github.com/godfreykaris/reddit-posts-scraper.git
cd reddit-posts-scraper
```


## 5.3 Fetching changes from the Repository
To fetch changes from the repository, follow the guideline below.
```bash
git pull origin main
```
If there are no changes, then you will see the message: 'Already up to date.'

If you do not get that message, you can solve the issue by running:
```bash
git reset --hard origin/main
```
A message like this means it has updated successfully: 
HEAD is now at ....

## 5.4 Install Dependencies

### 5.4.1 Create and activate a virtual environment:

#### For Linux/Mac OS:

```bash
python -m venv venv
source venv/bin/activate
```

#### For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
### 5.4.2 Update and upgrade pip which is the package installer for Python

```bash
python -m pip install --upgrade pip
```

### 5.4.3 Install the required Python packages:

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

### 5.4.4 Exiting the virtual environment
Type the following command and press Enter.
```bash
deactivate
```

# 6. Configuration
Ensure you have the chromedriver executable in your PATH or specify its location in the `DriverUtils` class if it's located elsewhere.
Adjust any configuration settings in `config.py` if necessary.


# 7. Usage
## 7.1 Command Line Interface
To start scraping posts from Reddit, use the following command:

```bash
python app.py -s <subreddit> -c <category> -l <limit> -o <output_path> -f <format> -v -p
```

### 7.1.1 Available Options

The following options are available to customize the scraping process:

- **`-s, --subreddit`**: (**Required**)  
  Name of the subreddit to scrape.

- **`-c, --categories`**: (**Optional**)  
  Categories to scrape (`hot`, `new`, `top`, or `all`; default is `hot`, `new` and `top`).

- **`-l, --limit`**: (**Optional**)  
  Limit on the number of posts to scrape per category (default is unlimited).

- **`-o, --output`**: (**Optional/Recommended**)  
  Output file path for the scraped posts (default is `scraped_posts.[format]` in the current directory).

- **`-f, --format`**: (**Optional**)  
  Output format for the scraped posts (`json`, `yaml`, `xml`; default is `json`).

- **`-v, --verbose`**: (**Optional**)  
  Enable verbose mode to print detailed processing information.
- **`-p, --ping`**: (**Optional**)
  Ping the subreddit to find out the number of available posts

## 7.2 Web Interface
The application can also be run using Flask, providing a web interface to initiate and monitor the scraping process.

Ensure the Flask application (app.py) is properly configured and dependencies are installed as described above.

### 7.2.1 Start the Flask application:

```bash
python app.py
```
Access the application through your web browser at http://localhost:5000.

## 8. Quitting
To exit the program you can use Ctrl + C.

## 9. Project Structure
```
reddit-scraper/
├── app.py
├── modules/
│   ├── colors.py
│   ├── config.py
│   ├── core.py
│   ├── driver_utils.py
│   ├── file_write_error.py
│   ├── posts_processing.py
│   ├── shared.py
|   ├── scraper.py
|   ├── threading_utils.py
├── static/
│   ├── styles.css
├── templates/
│   ├── index.html
├── chromedriver/
│   ├── chromedriver.exe (ensure this matches your Chrome version)
├── requirements.txt
├── README.md
```

## 10. Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

## 11. License
This project is licensed under the MIT License - see the LICENSE file for details.

## 12. Acknowledgments
- BeautifulSoup
- Selenium
- Flask
## 13. Additional Notes

1. **chromedriver:**

   Ensure that the chromedriver executable is compatible with your version of Google Chrome. You can download the appropriate version from the [ChromeDriver site](https://developer.chrome.com/docs/chromedriver/downloads).

2. **Configuration:**

   If the chromedriver is not placed in the default location, you may need to update the path in the `DriverUtils` class within `driver_utils.py`.
