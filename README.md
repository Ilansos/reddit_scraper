# Reddit Scraper

The Reddit Scraper is a Python script designed to collect and store data from Reddit, including subreddit posts, comments, and user information. The data is stored in a MongoDB database for further analysis and usage.

## Features

    Reddit API Integration: Uses PRAW (Python Reddit API Wrapper) for seamless interaction with Reddit's API.
    MongoDB Integration: Stores posts, comments, and user information in a MongoDB database.
    Logging: Logs all significant events and errors to a log file (reddit.log).

## Prerequisites

Ensure the following software packages and libraries are installed:

    Python 3.x
    MongoDB
    Python libraries:
        praw
        requests
        pytz
        langdetect
        pymongo

## Setup Instructions

### 1. Clone the Repository

First, clone this repository to your local machine using git:

```bash
git clone https://github.com/Ilansos/telegram_channel_scraper.git
cd <repository-directory>
```

### 2. Install Python Dependencies:

```bash
pip install -r requirements.txt
```

### 3. Install Translation Languages

Run the translator_install.py script to install the necessary languages for the translation library:

```bash
python translator_install.py
```

This script downloads and installs translation packages needed to convert content to English from various languages.


### 4. Obtain Reddit API credentials:

Create a Reddit account if you don't have one.
Go to Reddit Apps and log in.
Click on "Create App" or "Create Another App."
Choose the "script" type.
Fill out the form:
    Name: Name your app.
    Redirect URI: Set it to http://localhost:8080 (or any valid URL).
    Description: Optional description.
Submit the form, and note down the generated Client ID and Client Secret.

### 5. Configure MongoDB:

Ensure that MongoDB is installed and running on your system. By default, the scraper connects to MongoDB at mongodb://localhost:27017/. If your MongoDB setup differs, adjust the connection string that is located on the config.json file on the root directory of the project.

### 6. Configure the Scraper

Modify the config.json file that is located in the root directory the project with the following configuration parameters:

```json
{
    "mongo_uri": "mongodb://localhost:27017/",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "user_agent": "your_user_agent",
    "username": "your_username",
    "password": "your_password"
}
```

Replace the placeholders with the appropriate values.

### 7. Keywords file:

Modify the keywords.txt file in the root directory.

Add a list of keywords (one per line) to search Reddit for relevant posts.

The default content of keywords.txt are cybersecurity related keywords in English, Russian, Chinese and Farsi

## Usage

### Running the script:

To run the script, execute the following command:

```bash
python reddit.py
```

This will:

    Collect and store general Reddit statistics.
    Search for subreddits and posts across Reddit based on the keywords provided. Note that the script will not work without keywords specified in keywords.txt.
    Extract posts and their comments and store them in MongoDB.

    Logging:

    All actions, errors, and statuses are logged to reddit.log.

## Contributions

Feel free to contribute by:

    Reporting issues
    Submitting pull requests
    Suggesting improvements

## License

This project is licensed under the MIT License - see the LICENSE file for details.

### MIT License