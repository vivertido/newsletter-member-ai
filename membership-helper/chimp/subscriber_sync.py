from db import get_all_subscriber_hashes, add_new_subscribers, mark_missing_subscribers_as_deleted
from chimp.newsletters import fetch_and_export_subscribers
import json

def sync_subscribers_from_mailchimp(list_id):
    """
    Sync subscribers from a Mailchimp list with the database.

    Args:
        list_id (str): The Mailchimp list ID.
    """
    try:
        # Fetch the latest subscribers from Mailchimp
        exported_file = fetch_and_export_subscribers(list_id)
        if not exported_file:
            print("Failed to fetch subscribers from Mailchimp.")
            return

        with open(exported_file, "r") as f:
            latest_subscribers = json.load(f)

        # Prepare data for the database
        new_subscribers = []
        latest_hashes = []

        for subscriber in latest_subscribers:
            subscriber_hash = subscriber["id"]
            latest_hashes.append(subscriber_hash)

            # Prepare new subscriber data
            new_subscribers.append({
                "subscriber_hash": subscriber_hash,
                "status": "subscribed",
                "created_at": subscriber["timestamp_opt"]
            })

        # Add or update subscribers
        if new_subscribers:
            added_or_updated = add_new_subscribers(new_subscribers)
            print(f"Added or updated {len(new_subscribers)} subscribers.")
            print("New subscribers added or updated:")
            print([sub["subscriber_hash"] for sub in new_subscribers])

        # Mark missing subscribers as deleted
        removed = mark_missing_subscribers_as_deleted(latest_hashes)
        print(f"Marked {removed} subscribers as deleted.")
        print("Subscriber hashes marked as deleted:")
        print(removed)

        print("Subscriber sync complete.")
    except Exception as e:
        print(f"An error occurred during subscriber sync: {e}")