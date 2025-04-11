import feedparser
import time
import json
import os
from discord import SyncWebhook

# File to store last_entry IDs
LAST_ENTRIES_FILE = "last_entries.json"

# Load last_entry IDs from file if it exists
def load_last_entries():
    if os.path.exists(LAST_ENTRIES_FILE):
        with open(LAST_ENTRIES_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save last_entry IDs to file
def save_last_entries(last_entries):
    with open(LAST_ENTRIES_FILE, 'w') as f:
        json.dump(last_entries, f, indent=4)

# Get webhook URL from env or txt file
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

if not WEBHOOK_URL:
	try:
		with open('webhook.txt', 'r') as f:
			WEBHOOK_URL = f.read().strip()
	except FileNotFoundError:
		print("Error: webhook.txt not found. Please create it with your Discord webhook.")
		exit(1)

# Get user input for RSS feeds
feeds = []
i = 0
try:
	with open('feeds.txt', 'r') as f:
		for line in f:
			i += 1
			line = line.strip()
			if line: # Skip empty lines
				feeds.append({'name': "Feed" + str(i), 'url': line, 'last_entry': None})
except FileNotFoundError:
	print("Error: feeds.txt not found. Please create it with your RSS feeds")
	exit(1)

# Initialize last_entries dictionary
last_entries = load_last_entries()

# Set initial last_entry for each feed from the loaded data
for feed in feeds:
    feed['last_entry'] = last_entries.get(feed['name'], None)

# Create the webhook object
webhook = SyncWebhook.from_url(WEBHOOK_URL)

# Main loop to check feeds periodically
CHECK_INTERVAL = 1800  # 30 minutes

while True:
    start_time = time.time()
    for feed in feeds:
        try:
            print(f"Checking feed: {feed['name']}")
            parsed_feed = feedparser.parse(feed['url'])
            if parsed_feed.entries:
                latest_entry = parsed_feed.entries[0]
                if feed['last_entry'] is None or latest_entry.id != feed['last_entry']:
                    message = f"New post in {feed['name']}: {latest_entry.title}\n{latest_entry.link}"
                    webhook.send(message)
                    time.sleep(1)  # Avoid rate limiting
                    print(f"Posted to Discord: {message}")
                    feed['last_entry'] = latest_entry.id
                    last_entries[feed['name']] = feed['last_entry']
            else:
                print(f"No entries found in feed: {feed['name']}")
        except Exception as e:
            print(f"Error checking feed {feed['name']}: {e}")
    save_last_entries(last_entries)
    elapsed_time = time.time() - start_time
    sleep_time = max(0, CHECK_INTERVAL - elapsed_time)
    print(f"Cycle took {elapsed_time:.2f} seconds. Waiting {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)
