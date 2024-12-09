import streamlit as st
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError


API_KEY = st.secrets["API_KEY"]
MC_KEY = st.secrets["MC_KEY"]
SERVER_PREFIX = 'us2'  # Replace 'usX' with your specific Mailchimp server prefix
BASE_URL = f'https://{SERVER_PREFIX}.api.mailchimp.com/3.0/'
HEADERS = {
    'Authorization': f'Bearer {MC_KEY}'
    }


def get_member_activity(list_id, subscriber):
    """
    Fetch activity for a specific subscriber from a Mailchimp list.

    Args:
        list_id (str): The Mailchimp list ID.
        subscriber (str): The subscriber's unique hash.

    Returns:
        dict: Member activity response from Mailchimp, or an empty dict on error.
    """
    try:
        client = MailchimpMarketing.Client()
        client.set_config({
            "api_key": API_KEY,
            "server": SERVER_PREFIX
        })

        response = client.lists.get_list_member_activity(list_id, subscriber)
        return response

    except ApiClientError as error:
        print(f"Mailchimp API Client Error for Subscriber {subscriber}: {error.text}")
        return {}

    except Exception as e:
        print(f"An unexpected error occurred while fetching member activity for Subscriber {subscriber}: {e}")
        return {}