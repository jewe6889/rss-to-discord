# RSS to Discord Feed Poster

This script monitors RSS feeds and posts new updates to a Discord channel using a webhook.

## Features
- Supports RSS feeds from any source.
- Saves last checked entries to avoid reposting old entries on restart.
- Checks for updates automatically every 30 minutes if the script is left running.

## Requirements
- Python 3.x
- `requests`, `feedparser` and `discord.py` libraries

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jewe6889/rss-to-discord.git
   cd rss-to-discord

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate

3. **Install Dependencies**:
   ```bash
   pip install requests feedparser discord.py

4. **Fill out your webhook.txt and feeds.txt**:
   ```text
   - webhook.txt should contain the URL of your Discord webhook
   - feeds.txt should contain the URLs of your RSS feeds (one per line)

5. **Run the Script**:
   ```bash
   python rss_to_discord.py