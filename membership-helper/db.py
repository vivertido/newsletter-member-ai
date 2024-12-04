'''
db.py 
Holds all Stupabase logic
- fetch all newsletters
- add a newsletter

'''
import streamlit as st
from supabase import create_client

# Initialize Supabase client
SUPABASE_URL = st.secrets["SB_URL"]
SUPABASE_KEY = st.secrets["SB_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

"""
    <----------------------------------- NEWSLETTERS  ------------------------------------>
    
"""

def fetch_all_newsletters():
    """
    Fetch all newsletters from the database.

    Returns:
        list: A list of newsletter records.
    """
    response = supabase.table("newsletters").select("*").execute()
    if response.data:
        return response.data
    else:
        print("Error fetching newsletters:", response.error)
        return []
    
def newsletter_exists(list_id):
    """
    Check if a newsletter with the given list_id exists.

    Args:
        list_id (str): The Mailchimp list ID.

    Returns:
        bool: True if the newsletter exists, False otherwise.
    """
    response = supabase.table("newsletters").select("list_id").eq("list_id", list_id).execute()
    return len(response.data) > 0 if response.data else False

def add_newsletter(list_id, name):
    """
    Add a new newsletter to the database.

    Args:
        list_id (str): The Mailchimp list ID.
        name (str): The human-readable name of the newsletter.

    Returns:
        bool: True if the newsletter was added successfully, False otherwise.
    """
    if newsletter_exists(list_id):
        print(f"Newsletter with list_id '{list_id}' already exists.")
        return False

    response = supabase.table("newsletters").insert(
        {"list_id": list_id, "name": name, "subscriber_count": 0, "last_synced": None}
    ).execute()

    if response.data:
        print(f"Newsletter '{name}' added successfully.")
        return True
    else:
        print("Error adding newsletter:", response.error)
        return False
    
def update_newsletter_subscriber_count(list_id, subscriber_count, last_synced):
    """
    Update the subscriber count and last synced timestamp for a newsletter.

    Args:
        list_id (str): The Mailchimp list ID.
        subscriber_count (int): The updated subscriber count.
        last_synced (str): The timestamp of the last sync in ISO format.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        response = supabase.table("newsletters").update(
            {"subscriber_count": subscriber_count, "last_synced": last_synced}
        ).eq("list_id", list_id).execute()

        if response.data:
            print(f"Newsletter {list_id} updated successfully.")
            return True
        else:
            print(f"Error updating newsletter {list_id}: {response.error}")
            return False

    except Exception as e:
        print(f"An unexpected error occurred while updating newsletter {list_id}: {e}")
        return False

"""
      <-----------------------------------  MEMBERS / SUBSCRIBERS  ------------------------------------>
    
"""

def get_total_subscribers():
    """
    Fetch the total count of subscribers in the database.

    Returns:
        int: The total number of subscribers.
    """
    response = supabase.table("subscribers").select("id", count="exact").execute()
    if response.data:
        return response.count
    else: 
        print("Error fetching total subscribers:", response.error)
        return 0

def get_all_subscriber_hashes():
    """
    Fetch all subscriber hashes from the database.

    Returns:
        list: A list of subscriber hashes.
    """
    response = supabase.table("subscribers").select("subscriber_hash").execute()
    if response.data:
        return [row["subscriber_hash"] for row in response.data]
    else:
        print("Error fetching subscriber hashes:", response.error)
        return []

def fetch_subscribers(limit=10, created_after=None):
    """
    Fetch subscribers sorted by total_clicks, filtered by creation date.

    Args:
        limit (int): The maximum number of results to fetch.
        created_after (str, optional): Fetch members created after this date (ISO format).

    Returns:
        list: A list of subscribers.
    """
    query = supabase.table("subscribers").select("id, subscriber_hash, total_clicks, created_at")

    if created_after:
        query = query.gte("created_at", created_after)

    query = query.order("total_clicks", desc=True).limit(limit)

    response = query.execute()
    if response.data:
        return response.data
    else:
        print("Error fetching subscribers:", response.error)
        return []
    

def add_new_subscribers(subscribers):
    """
    Add new subscribers to the database, updating existing ones if they already exist.

    Args:
        subscribers (list): List of subscriber dictionaries to insert.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        response = supabase.table("subscribers").upsert(
            subscribers,
            on_conflict="subscriber_hash"  # Specify the unique constraint
        ).execute()

        if response.data:
            print(f"Added or updated {len(response.data)} subscribers.")
            return True
        else:
            print("Error adding or updating subscribers:", response.error)
            return False
    except Exception as e:
        print(f"An unexpected error occurred while adding or updating subscribers: {e}")
        return False
    

    
def remove_missing_subscribers(subscriber_hashes_to_keep, batch_size=100):
    """
    Remove subscribers from the database whose hashes are not in the given list.

    Args:
        subscriber_hashes_to_keep (list): List of current subscriber hashes to keep.
        batch_size (int): Number of hashes to process per batch.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        total_removed = 0
        # Fetch all subscriber hashes currently in the database
        response = supabase.table("subscribers").select("subscriber_hash").execute()
        if not response.data:
            print("No subscribers found in the database to remove.")
            return True

        current_hashes_in_db = {row["subscriber_hash"] for row in response.data}

        # Identify hashes to delete
        hashes_to_delete = list(current_hashes_in_db - set(subscriber_hashes_to_keep))
        print(f"Total hashes to delete: {len(hashes_to_delete)}")

        # Process deletion in batches
        total_batches = (len(hashes_to_delete) - 1) // batch_size + 1
        for i in range(total_batches):
            batch = hashes_to_delete[i * batch_size : (i + 1) * batch_size]
            try:
                response = supabase.table("subscribers").delete().in_(
                    "subscriber_hash", batch
                ).execute()

                removed_count = len(response.data) if response.data else 0
                total_removed += removed_count
                print(f"Batch {i + 1}: Removed {removed_count} subscribers.")
            except Exception as e:
                print(f"Error removing subscribers in batch {i + 1}: {e}")
                return False

        print(f"Total subscribers removed: {total_removed}")
        return True
    except Exception as e:
        print(f"An unexpected error occurred while removing subscribers: {e}")
        return False
    
def mark_missing_subscribers_as_deleted(subscriber_hashes_to_keep):
    """
    Mark subscribers as 'deleted' in the database if their hashes are not in the given list.

    Args:
        subscriber_hashes_to_keep (list): List of current subscriber hashes to keep.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Fetch all subscriber hashes currently in the database
        response = supabase.table("subscribers").select("subscriber_hash").execute()
        if not response.data:
            print("No subscribers found in the database to mark as deleted.")
            return True

        current_hashes_in_db = {row["subscriber_hash"] for row in response.data}
        print(f"Current hashes in DB: {len(current_hashes_in_db)}")

        # Identify hashes to mark as deleted
        hashes_to_mark_deleted = list(current_hashes_in_db - set(subscriber_hashes_to_keep))
        print(f"Hashes to keep: {len(subscriber_hashes_to_keep)}")
        print(f"Hashes to mark as deleted: {len(hashes_to_mark_deleted)}")

        if not hashes_to_mark_deleted:
            print("No subscribers to mark as deleted.")
            return True

        # Mark these hashes as deleted
        response = supabase.table("subscribers").update(
            {"status": "deleted"}
        ).in_("subscriber_hash", hashes_to_mark_deleted).execute()

        if response.data:
            print(f"Marked {len(response.data)} subscribers as deleted.")
            return True
        else:
            print("Error marking subscribers as deleted:", response.error)
            return False
    except Exception as e:
        print(f"An unexpected error occurred while marking subscribers as deleted: {e}")
        return False






"""
     <-----------------------------------   CLICK ACTIVITY ------------------------------------>
    
"""


def fetch_click_activity(start_date=None, end_date=None, newsletter=None, limit=100):
    """
    Fetch click activity from the database, with optional filters.

    Args:
        start_date (str): Start date to filter click activity (YYYY-MM-DD).
        end_date (str): End date to filter click activity (YYYY-MM-DD).
        newsletter (str): Newsletter name or ID to filter results.
        limit (int): Maximum number of results to fetch.

    Returns:
        list: A list of click activity records, or an empty list on error.
    """
    try:
        query = supabase.table("click_activity").select("id, subscriber_hash, clicked_headline, newsletter, click_date")
        
        if start_date:
            query = query.gte("click_date", start_date)
        if end_date:
            query = query.lte("click_date", end_date)
        if newsletter:
            query = query.eq("newsletter", newsletter)

        query = query.order("click_date", desc=True).limit(limit)
        response = query.execute()

        if response.data:
            return response.data
        else:
            print("Error fetching click activity:", response.error)
            return []

    except Exception as e:
        print(f"An unexpected error occurred while fetching click activity: {e}")
        return []
    
def fetch_most_popular_headline(start_date=None, end_date=None):
    """
    Fetch the most popular headline based on the number of clicks.

    Args:
        start_date (str): Start date to filter click activity (YYYY-MM-DD).
        end_date (str): End date to filter click activity (YYYY-MM-DD).

    Returns:
        dict: The most popular headline and its click count, or None on error.
    """
    try:
        query = supabase.table("click_activity").select(
            "clicked_headline, count(clicked_headline) as click_count", count="exact"
        )
        
        if start_date:
            query = query.gte("click_date", start_date)
        if end_date:
            query = query.lte("click_date", end_date)

        query = query.group("clicked_headline").order("click_count", desc=True).limit(1)
        response = query.execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            print("No data found or error occurred:", response.error)
            return None

    except Exception as e:
        print(f"An unexpected error occurred while fetching the most popular headline: {e}")
        return None
    
def get_all_newsletter_names():
    """
    Fetch all newsletters and return a dictionary mapping list_id to name.

    Returns:
        dict: A dictionary where the keys are `list_id` and the values are `name`.
    """
    response = supabase.table("newsletters").select("list_id, name").execute()
    if response.data:
        return {n["list_id"]: n["name"] for n in response.data}
    else:
        print("Error fetching newsletters:", response.error)
        return {}