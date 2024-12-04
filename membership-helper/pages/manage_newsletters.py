import streamlit as st
from db import fetch_all_newsletters, add_newsletter, update_newsletter_subscriber_count
from chimp.subscriber_sync import sync_subscribers_from_mailchimp

from chimp import newsletters as nl 
from datetime import datetime
import json
 

 

if not st.session_state.get("authenticated", False):
    st.error("You must log in to access this page.")
   
    st.switch_page("pages/login.py")
    st.stop()  # Stop further execution of the page

st.title("Newsletter Setup")
st.markdown("Manage your newsletters: Add new ones and view existing details.")

tab1, tab2 = st.tabs(["Add New Newsletter", "Existing Newsletters"])

# Tab 1: Add New Newsletter
with tab1:
    st.subheader("Add a New Newsletter")
    list_id = st.text_input("Enter Newsletter List ID")
    name = st.text_input("Enter Newsletter Name")
    
    if st.button("Add Newsletter"):
        if list_id and name:
            if add_newsletter(list_id, name):
                st.success(f"Newsletter '{name}' added successfully!")
            else:
                st.warning(f"Newsletter with List ID '{list_id}' already exists.")
        else:
            st.error("Please provide both List ID and Name.")

# Tab 2: View Existing Newsletters
with tab2:
    st.subheader("Existing Newsletters")
    newsletters = fetch_all_newsletters()
    
    if newsletters:
        st.write("Here are the newsletters currently in the database:")

        for newsletter in newsletters:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 2, 2])
            col1.write(newsletter["name"])
            col2.write(newsletter["list_id"])
            col3.write(newsletter.get("subscriber_count", 0))

            # Format the `last_synced` timestamp
            last_synced_raw = newsletter.get("last_synced")
            last_synced_formatted = (
                datetime.fromisoformat(last_synced_raw).strftime("%B %d, %Y %I:%M %p")
                if last_synced_raw and last_synced_raw != "Never"
                else "Never"
            )
            col4.write(last_synced_formatted)

            # Sync button logic
            if col5.button("Sync", key=f"sync_{newsletter['list_id']}"):
                with st.spinner(f"Syncing data for {newsletter['name']}..."):
                    try:
                        # Trigger the sync process
                        exported_file = sync_subscribers_from_mailchimp(newsletter["list_id"])

                        if exported_file:
                            # Update the subscriber count using the number of records in the JSON file
                            with open(exported_file, "r") as f:
                                subscribers = json.load(f)
                                subscriber_count = len(subscribers)

                            now = datetime.now().isoformat()
                            update_newsletter_subscriber_count(newsletter["list_id"], subscriber_count, now)

                            st.success(f"Newsletter '{newsletter['name']}' synced successfully! Subscriber count updated to {subscriber_count}.")
                        else:
                            st.error(f"Failed to sync newsletter '{newsletter['name']}'. Please try again.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
    else:
        st.info("No newsletters found.")
