# Nurkz News Bot

## Overview

This Python script implements a Telegram bot that provides users with the latest news from the Nur.kz website. The bot periodically fetches news updates, stores them in a MongoDB database, and sends notifications to users about new articles. Users can request news updates and navigate through paginated news articles.

## Features

1. **News Fetching and Notification:**
   - The script fetches news articles from the Nur.kz website periodically.
   - New articles are stored in a MongoDB database, and notifications about them are sent to all users who have interacted with the bot.
   
2. **Pagination:**
   - Users can navigate through paginated news articles using inline keyboard pagination.
   
3. **User Interaction:**
   - Users can start the bot and request news updates by clicking the "News" button in the bot's menu.
   - The bot records the time of users' interactions and updates it with each interaction.

## Dependencies

- `asyncio`: Asynchronous I/O library for running concurrent tasks.
- `logging`: Python logging module for logging messages.
- `requests`: HTTP library for making requests to web servers.
- `re`: Regular expression operations for pattern matching.
- `json`: Module for encoding and decoding JSON data.
- `BeautifulSoup`: Library for web scraping HTML and XML files.
- `aiogram`: Library for developing Telegram bots.
- `pymongo`: MongoDB driver for Python.

## Setup

1. **Telegram Bot Token:**
   - Obtain a Telegram Bot Token by creating a new bot using the BotFather on Telegram. Replace the `TOKEN` variable in the `config.py` file with your bot token.

2. **MongoDB:**
   - Install MongoDB and start the MongoDB service.
   - Ensure that MongoDB is running on `localhost` at port `27017`.
   
3. **Dependencies Installation:**
   - Install the required Python dependencies using `pip install -r requirements.txt`.

4. **Execution:**
   - Run the Python script `news_bot.py`.
   - Interact with the bot by starting it and clicking the "News" button in the menu.

## Usage

1. Start the bot by sending the `/start` command.
2. Click the "News" button in the menu to request news updates.
3. Navigate through news articles using pagination buttons.
4. Click on the "Смотреть на сайте" button to view the full article on the Nur.kz website.

## Notes

- The script fetches news updates from the Nur.kz website at intervals of 60 seconds.
- News articles are stored in a JSON file (`news_dict.json`) and a MongoDB collection (`users`).
- Pagination allows users to view multiple news articles in a sequential manner.


