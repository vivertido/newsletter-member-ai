from utils import extract_slug_from_url, get_post_details
from chimp.member_clicks import get_member_activity
from db import update_total_clicks, insert_click_activity


def process_subscriber_clicks(list_id, subscribers):
    """
    Process click activity for each subscriber and store it in the database.

    Args:
        list_id (str): The newsletter list ID.
        subscribers (list): List of subscriber hashes.

    Returns:
        dict: Summary of processed, skipped, and error counts.
    """
    processed_count = 0
    skipped_count = 0
    error_count = 0
    processed_slugs = set()

    for subscriber_hash in subscribers:
        activity = get_member_activity(list_id, subscriber_hash)

        if not activity or "activity" not in activity:
            print(f"No activity data for Subscriber {subscriber_hash}")
            skipped_count += 1
            continue

        # Filter for click actions
        clicks = [act for act in activity["activity"] if act["action"] == "click"]

        # Track total clicks for the subscriber
        total_clicks = 0

        for click in clicks:
            # Extract slug and post details
            slug = extract_slug_from_url(click.get("url", ""))
            if not slug or slug == "unknown" or slug in processed_slugs:
                print(f"Skipped invalid or duplicate slug for Subscriber {subscriber_hash}: {slug}")
                skipped_count += 1
                continue

            post_details = get_post_details(slug, list_id)
            if not post_details:
                print(f"Skipped slug with no valid post details for Subscriber {subscriber_hash}: {slug}")
                skipped_count += 1
                continue

            # Store click activity
            try:
                insert_click_activity(
                    subscriber_hash=subscriber_hash,
                    clicked_headline=post_details,
                    newsletter=list_id,
                    click_date=click["timestamp"]
                )
                processed_slugs.add(slug)
                total_clicks += 1
                processed_count += 1
            except Exception as e:
                print(f"Error inserting click activity for Subscriber {subscriber_hash}: {e}")
                error_count += 1

        # Update total clicks for the subscriber
        try:
            update_total_clicks(subscriber_hash, total_clicks)
        except Exception as e:
            print(f"Error updating total clicks for Subscriber {subscriber_hash}: {e}")
            error_count += 1

    return {
        "processed_count": processed_count,
        "skipped_count": skipped_count,
        "error_count": error_count
    }