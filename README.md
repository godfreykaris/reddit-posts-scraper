# Reddit Scraper

A web scraping application designed to extract posts from a specified subreddit. The application uses Selenium and BeautifulSoup to navigate and parse the content of Reddit posts, and saves the results to a JSON file.

## Features

- Extracts posts from a specified subreddit based on user input.
- Allows selection of the number of posts to be scraped.
- Provides options to select categories like "hot", "new", and "top" for scraping.
- If fewer posts are available than requested, it scrapes the maximum available posts.
- Displays real-time progress of the scraping process.
- Includes a user interface for easy interaction.

## Technologies Used

- Python
- Flask
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

## Running the Application
To start the application, run:

```bash
python app.py
```

Open your browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) to access the application.

## Usage
1. Enter the subreddit name and the number of posts you want to scrape.
2. Click "Start Extracting" to begin the scraping process.
3. Monitor the progress through the progress bar and status text.
4. Click "Quit Application" to stop the scraping and close the application.

## Project Structure
```
reddit-scraper/
├── app.py
├── modules/
│   ├── config.py
│   ├── driver_utils.py
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
