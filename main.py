import argparse
import time
from utils import load_last_entries, save_last_entries, process_feed
from discord import SyncWebhook

# Constants
LAST_ENTRIES_FILE = "last_entries.json"
CHECK_INTERVAL = 600  # 10 minutes

# Read Discord webhook URL from file
with open('webhook.txt', 'r') as f:
    WEBHOOK_URL = f.read().strip()

# Read RSS feeds from feeds.txt
feeds = []
i = 0
try:
    with open('feeds.txt', 'r') as f:
        for line in f:
            i += 1
            line = line.strip()
            if line:  # Skip empty lines
                feeds.append({'name': "Feed" + str(i), 'url': line, 'last_entry': None})
except FileNotFoundError:
    print("Error: feeds.txt not found. Please create it with your RSS feeds")
    exit(1)

# Load existing last_entries
last_entries = load_last_entries(LAST_ENTRIES_FILE)

# Argument parsing
parser = argparse.ArgumentParser(description="RSS to Discord Feed Poster")
parser.add_argument('--delay', type=float, default=1.0, help='Delay in seconds to avoid rate-limiting')
parser.add_argument('--start-from', type=int, default=0, help='Index of the first feed to check (0-based)')
args = parser.parse_args()

# Validate delay
delay = args.delay
if delay < 0:
    print("Error: Delay cannot be negative.")
    exit(1)

# Validate start_from
start_from = args.start_from
if start_from < 0 or start_from >= len(feeds):
    print(f"Error: --start-from index {start_from} is out of range. Must be between 0 and {len(feeds) - 1}.")
    exit(1)

# Set initial last_entry for each feed from the loaded data
for feed in feeds:
    feed['last_entry'] = last_entries.get(feed['name'], None)

# Create the webhook object
webhook = SyncWebhook.from_url(WEBHOOK_URL)

# Main loop
while True:
    start_time = time.time()

    # Check if last_entries.json has fewer entries than feeds.txt
    total_feeds = len(feeds)
    recorded_entries = len(last_entries)

    if recorded_entries < total_feeds:
        print(f"JSON has {recorded_entries} entries, but feeds.txt has {total_feeds}. Populating missing feeds...")
        for feed in feeds[start_from:]:
            if feed['name'] not in last_entries:
                process_feed(feed, webhook, last_entries, delay, LAST_ENTRIES_FILE)
                time.sleep(delay)  # Additional rate limiting
    else:
        print("All feeds have last_entry recorded. Checking for updates...")
        for feed in feeds[start_from:]:
            process_feed(feed, webhook, last_entries, delay, LAST_ENTRIES_FILE)

    # Calculate elapsed time and sleep accordingly
    elapsed_time = time.time() - start_time
    sleep_time = max(0, CHECK_INTERVAL - elapsed_time)
    print(f"Cycle took {elapsed_time:.2f} seconds. Waiting {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)
