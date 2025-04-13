import json
import os
import time
import feedparser

def load_last_entries(file_path):
    """Load last_entry IDs from a JSON file if it exists."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_last_entries(last_entries, file_path):
    """Save last_entry IDs to a JSON file, sorted by feed number."""
    sorted_entries = dict(sorted(
        last_entries.items(),
        key=lambda x: int(x[0].split("Feed ")[-1]) if "Feed " in x[0] else -1
    ))
    with open(file_path, 'w') as f:
        json.dump(sorted_entries, f, indent=4)

def process_feed(feed, webhook, last_entries, delay, file_path):
    """Process a single feed, post to Discord if there's a new entry, and update last_entries."""
    try:
        print(f"Checking feed: {feed['name']}")
        parsed_feed = feedparser.parse(feed['url'])
        time.sleep(delay)  # Avoid rate limiting
        if parsed_feed.entries:
            latest_entry = parsed_feed.entries[0]
            if feed['last_entry'] is None or feed['last_entry'] == "empty" or latest_entry.id != feed['last_entry']:
                message = f"New post in {feed['name']}: {latest_entry.title}\n{latest_entry.link}"
                webhook.send(message)
                print(f"Posted to Discord: {message}")
                feed['last_entry'] = latest_entry.id
                last_entries[feed['name']] = feed['last_entry']
                save_last_entries(last_entries, file_path)  # Save after each post
        else:
            if feed['last_entry'] != "empty":
                feed['last_entry'] = "empty"
                last_entries[feed['name']] = "empty"
                save_last_entries(last_entries, file_path)  # Save when marking as empty
            print(f"No entries found in feed: {feed['name']}")
    except Exception as e:
        print(f"Error checking feed {feed['name']}: {e}")
