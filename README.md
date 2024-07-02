# Reddit Scraper

A web scraping application designed to extract posts from a specified subreddit. The application uses Selenium and BeautifulSoup to navigate and parse the content of Reddit posts, and saves the results to a JSON file.

## Features

- **Scrapes Multiple Categories**: Allows scraping from multiple categories such as 'hot', 'new', 'top', or all categories combined.
- **Multi-threaded Scraping**: Utilizes threads for concurrent scraping when either multiple categories are selected or no specific category is specified, optimizing performance.
- **Output Formats**: Supports output formats including JSON and YAML.
- **Dynamic Output File Naming**: Automatically names output files based on specified file path and optional format.
- **Progress Monitoring**: Provides real-time progress updates during the scraping process.
- **Error Handling**: Handles errors gracefully, skipping invalid categories and displaying relevant messages.
- **Customizable Limits**: Allows setting a limit on the number of posts to scrape.
- **Verbose Mode**: Enables verbose mode to print detailed processing information.


## Technologies Used

- Python
- Selenium
- BeautifulSoup

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.8 or later.
- You have `pip` installed.
- You have Google Chrome installed.
- You have downloaded the ChromeDriver that matches your Chrome version and placed it in a directory accessible to your PATH.

## Setup

### Clone the Repository

```sh
git clone https://github.com/godfreykaris/reddit-posts-scraper.git
cd reddit-scraper
```

## Install Dependencies

## Setting Up the Environment

### Create and activate a virtual environment:

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

## Install the required Python packages:

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Configuration
Ensure you have the chromedriver executable in your PATH or specify its location in the `DriverUtils` class if it's located elsewhere.
Adjust any configuration settings in `config.py` if necessary.


## Usage
## Command Line Interface
To start scraping posts from Reddit, use the following command:

```bash
python app.py -s <subreddit> -c <category> -l <limit> -o <output_path> -f <format> -v
```

### Available Options

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
  Output format for the scraped posts (`json`, `yaml`; default is `json`).

- **`-v, --verbose`**: (**Optional**)  
  Enable verbose mode to print detailed processing information.

## Web Interface
The application can also be run using Flask, providing a web interface to initiate and monitor the scraping process.

Ensure the Flask application (app.py) is properly configured and dependencies are installed as described above.

### Start the Flask application:

```bash
python app.py
```
Access the application through your web browser at http://localhost:5000.

## Quitting
You can quit the app by pressing CTRL + C

## Project Structure
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

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- BeautifulSoup
- Selenium
- Flask
## Additional Notes

1. **chromedriver:**

   Ensure that the chromedriver executable is compatible with your version of Google Chrome. You can download the appropriate version from the [ChromeDriver site](https://developer.chrome.com/docs/chromedriver/downloads).

2. **Configuration:**

   If the chromedriver is not placed in the default location, you may need to update the path in the `DriverUtils` class within `driver_utils.py`.
