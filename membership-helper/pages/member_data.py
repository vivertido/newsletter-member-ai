import streamlit as st
from db import get_total_subscribers, fetch_subscribers
from datetime import datetime, timedelta

st.title("Member Data")
st.markdown("Fetch and display subscriber data based on criteria.")

# Display total subscribers
total_subscribers = get_total_subscribers()
st.write(f"**Total Subscribers:** {total_subscribers}")

# Filters for fetching subscribers
st.subheader("Filters")
number_of_results = st.number_input("Number of Results", min_value=1, max_value=total_subscribers, value=10)
created_after = st.date_input(
    "Created After",
    value=(datetime.now() - timedelta(days=30)),  # Default to 30 days ago
    min_value=datetime(2000, 1, 1),
    max_value=datetime.now()
)

# Fetch subscribers on button click
if st.button("Get Subscribers"):
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