import streamlit as st
from db import fetch_click_activity, fetch_most_popular_headline, fetch_most_popular_headline, fetch_all_newsletters, get_all_newsletter_names
from datetime import datetime, timedelta

st.title("Click Activity")
st.markdown("Analyze and explore click activity from newsletters.")

# Filters for fetching click activity
st.subheader("Filters")

# Fetch newsletters for the dropdown
newsletters = fetch_all_newsletters()
newsletter_options = {n["name"]: n["list_id"] for n in newsletters} if newsletters else {}


if newsletter_options:
    selected_newsletter = st.selectbox("Select a Newsletter", options=newsletter_options.keys())
else:
    st.warning("No newsletters found. Please add newsletters in the setup page.")
    selected_newsletter = None

start_date = st.date_input("Start Date", value=(datetime.now() - timedelta(days=7)), max_value=datetime.now())
end_date = st.date_input("End Date", value=datetime.now(), max_value=datetime.now())
limit = st.number_input("Number of Results", min_value=1, max_value=1000, value=100)


# Fetch click activity

newsletter_names = get_all_newsletter_names()

if st.button("Get Click Activity"):
    if selected_newsletter:
        try:
            click_activity = fetch_click_activity(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                newsletter=newsletter_options[selected_newsletter],
                limit=limit,
            )

            if click_activity:
                # Map newsletter IDs to names and prepare the display data
                display_data = [
                    {
                        "Headline": item["clicked_headline"],
                        "Newsletter": newsletter_names.get(item["newsletter"], "Unknown"),
                        "Click Date": item["click_date"],
                    }
                    for item in click_activity
                ]

                st.write(f"Fetched {len(display_data)} click activity records:")
                st.table(display_data)
            else:
                st.info("No click activity found for the given criteria.")
        except Exception as e:
            st.error(f"An error occurred while fetching click activity: {e}")
    else:
        st.warning("Please select a newsletter.")


# Fetch the most popular headline
if st.button("Get Most Popular Headline"):
    if selected_newsletter:
        try:
            popular_headline = fetch_most_popular_headline(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
            )

            if popular_headline:
                st.write("### Most Popular Headline")
                st.write(f"**Headline:** {popular_headline['clicked_headline']}")
                st.write(f"**Click Count:** {popular_headline['click_count']}")
            else:
                st.info("No headline data found for the given criteria.")
        except Exception as e:
            st.error(f"An error occurred while fetching the most popular headline: {e}")
    else:
        st.warning("Please select a newsletter.")
