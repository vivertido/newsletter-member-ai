
import streamlit as st
from db import update_newsletter_subscriber_count
from datetime import datetime
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
import json


"""
Getting List data from mailchimp
"""


API_KEY = st.secrets["API_KEY"]
MC_KEY = st.secrets["MC_KEY"]
SERVER_PREFIX = 'us2'  # Replace 'usX' with your specific Mailchimp server prefix
BASE_URL = f'https://{SERVER_PREFIX}.api.mailchimp.com/3.0/'
HEADERS = {
    'Authorization': f'Bearer {MC_KEY}'
    }


def fetch_and_export_subscribers(list_id, temp_dir="temp"):
    """
    Fetch subscribers from a Mailchimp list and export as a JSON file.

    Args:
        list_id (str): The Mailchimp list ID.
        temp_dir (str): Directory to store the exported JSON file.

    Returns:
        str: Path to the exported JSON file, or None if an error occurred.
    """
    try:
        # Mailchimp API configuration
        MC_KEY = st.secrets["MC_KEY"]
        SERVER_PREFIX = 'us2'

        client = MailchimpMarketing.Client()

        client.set_config({
            "api_key": MC_KEY,
            "server": SERVER_PREFIX
        })

        # Prepare for fetching
        response_list = []
        offset = 0
        count = 100  # Number of records to fetch per request

        fields = [
            "members.id",
            "members.status",
            "members.stats.avg_open_rate",
            "members.stats.avg_click_rate",
            "members.timestamp_opt",
            "members.tags"
        ]

        # Fetch data in batches
        while True:
            response = client.lists.get_list_members_info(
                list_id,
                count=count,
                offset=offset,
                fields=fields,
                status="subscribed"
            )

            response_list.extend(response["members"])
            
            #print(len(response_list))

            # Check if all members have been fetched
            if len(response["members"]) < count:
                break

            offset += count  # Move to the next batch

        # Export data to a JSON file
       # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
       # output_path = f"{temp_dir}/subscribers_{list_id}.json"
        output_file = f"{temp_dir}/subscribers_{list_id}.json"


        with open(output_file, "w") as f:
            json.dump(response_list, f, indent=4)

        print(f"Exported subscribers to {output_file}")
        return output_file

    except ApiClientError as error:
        print(f"Mailchimp API Error: {error.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while exporting subscribers: {e}")
        return None

def get_mc_subscribers_by_list_id(list_id):
    """
     Get the nunmber of subscribers from a given list id
    """
    try:
        MC_KEY = st.secrets["MC_KEY"]
        SERVER_PREFIX = 'us2'
            
        client = MailchimpMarketing.Client()
        client.set_config({
                "api_key": MC_KEY,
                "server": SERVER_PREFIX
            })
        
        # Fetch the total count of subscribed members
        response = client.lists.get_list(list_id, fields=["stats.member_count"])
        if "stats" in response and "member_count" in response["stats"]:
            return response["stats"]["member_count"]
        else:
            print(f"No stats found for list {list_id}.")
            return 0

   
    except Exception as e:
        print(f"An unexpected error occurred while getting subscriber count foruk newsletter {list_id}: {e}")
        return False
    

def sync_newsletter_data(list_id):
    """
    Sync the data for a specific newsletter.

    Args:
        list_id (str): The Mailchimp list ID to sync.

    Returns:
        bool: True if the sync was successful, False otherwise.
    """
    # Fetch updated data from Mailchimp API (dummy logic here for example)
    try:
       
        now = datetime.now().isoformat()
 

         

    except Exception as e:
        print(f"An unexpected error occurred while syncing newsletter {list_id}: {e}")
        return False