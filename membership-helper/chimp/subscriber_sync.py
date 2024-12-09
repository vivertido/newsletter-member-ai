from db import get_all_subscriber_hashes, add_new_subscribers, mark_missing_subscribers_as_deleted, sync_subscriber_list_id
from chimp.newsletters import fetch_and_export_subscribers
import json

def sync_subscribers_from_mailchimp(list_id):
    """
    Sync subscribers from a Mailchimp list with the database.

    Args:
        list_id (str): The Mailchimp list ID.

    Returns:
        str: Path to the exported JSON file.
    """
    print(f"Attempting a sync of list ID {list_id}")
    try:
        # Fetch the latest subscribers from Mailchimp
        exported_file = fetch_and_export_subscribers(list_id)
        if not exported_file:
            print("Failed to fetch subscribers from Mailchimp.")
            return None

        with open(exported_file, "r") as f:
            latest_subscribers = json.load(f)

        # Prepare data for the database
        new_subscribers = []
        latest_hashes = []  # Track all subscriber hashes from this sync

        for subscriber in latest_subscribers:
            subscriber_hash = subscriber["id"]
            print(f"appending {subscriber_hash}. ")
            latest_hashes.append(subscriber_hash)

            # Update or append the list_id
            sync_subscriber_list_id(subscriber_hash, list_id)

            # Prepare new subscriber data
            new_subscribers.append({
                "subscriber_hash": subscriber_hash,
                "list_id": [list_id],  # Ensure new entries have list_id as an array
                "status": "subscribed",
                "created_at": subscriber["timestamp_opt"]
            })

        # Add or update subscribers
        if new_subscribers:
            add_new_subscribers(new_subscribers)

        # Mark missing subscribers as deleted
        #removed = mark_missing_subscribers_as_deleted(latest_hashes)
       # print(f"Marked {len(removed)} subscribers as deleted.")

        print("Subscriber sync complete.")
        return exported_file
    except Exception as e:
        print(f"An error occurred during subscriber sync: {e}")
        return None