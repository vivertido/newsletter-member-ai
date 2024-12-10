import streamlit as st
from db import get_total_subscribers, fetch_subscribers, fetch_subscribers_sorted_by_clicks, fetch_all_newsletters
from chimp.member_clicks import get_member_activity
from datetime import datetime, timedelta
from utils import extract_slug_from_url, get_post_details, clean_headline
from tasks import process_click_activity


st.title("Member Data")
st.markdown("Fetch and display subscriber data based on criteria.")

# Display total subscribers
total_subscribers = get_total_subscribers()
st.write(f"**Total Subscribers:** {total_subscribers}")

# Tabs for different filters
tab1, tab2 = st.tabs(["By Date Created", "Explore member clicks"])

# Tab 1: Search by Date Created
with tab1:
    st.subheader("Search by Date Created")
    number_of_results = st.number_input("Number of Results", min_value=1, max_value=total_subscribers, value=10)
    created_after = st.date_input(
        "Created After",
        value=(datetime.now() - timedelta(days=30)),  # Default to 30 days ago
        min_value=datetime(2000, 1, 1),
        max_value=datetime.now()
    )

    if st.button("Get Subscribers by Date"):
        # Convert date input to ISO format
        created_after_iso = created_after.isoformat()

        # Fetch subscribers
        subscribers = fetch_subscribers(limit=number_of_results, created_after=created_after_iso)

        # Display results
        if subscribers:
            for subscriber in subscribers:
                if subscriber.get("created_at"):
                    subscriber["created_at"] = datetime.fromisoformat(subscriber["created_at"]).strftime("%B %d, %Y %I:%M %p")
            
            st.write(f"Fetched {len(subscribers)} subscribers:")
            st.table(subscribers)
        else:
            st.info("No subscribers found matching the criteria.")

with tab2:
    st.subheader("Debug Click Activity")

    # Input for Subscriber Hash and List ID
    subscriber_hash = st.text_input("Enter Subscriber Hash")
    list_id = st.text_input("Enter List ID")

    # Submit Button
    if st.button("Fetch Click Activity"):
        if not subscriber_hash or not list_id:
            st.error("Please enter both subscriber hash and list ID.")
        else:
            # Fetch click activity for the subscriber
            result = process_click_activity(list_id, subscriber_hash)

            if result.get("processed_count", 0) > 0:
                    st.success(f"Processed {result['processed_count']} clicks for subscriber {subscriber_hash}.")
                    if result.get("skipped_count", 0) > 0:
                        st.warning(f"Skipped {result['skipped_count']} invalid clicks for subscriber {subscriber_hash}.")
                    if result.get("error_count", 0) > 0:
                        st.error(f"Encountered {result['error_count']} errors for subscriber {subscriber_hash}.")

            st.success("Finished processing click activity.")

            