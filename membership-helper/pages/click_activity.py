import streamlit as st
from db import fetch_click_activity, insert_click_activity, update_total_clicks, fetch_most_popular_headline, fetch_most_popular_headline, fetch_subscribers_sorted_by_clicks, fetch_all_newsletters, get_all_newsletter_names
from datetime import datetime, timedelta
from tasks import process_subscriber_clicks
from chimp.member_clicks import get_member_activity
from utils import extract_slug_from_url, get_post_details, clean_headline



st.title("Click Activity")
st.markdown("Analyze and explore click activity from newsletters.")

tab1, tab2 = st.tabs(["Explore Click Activity", "Fetch New Click Activity"])

with tab1:
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
                # Call fetch_click_activity
                click_activity = fetch_click_activity(
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    newsletter=newsletter_options[selected_newsletter],
                    limit=limit,
                )

                # Check if data is returned
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

                    # Display the results
                    st.write(f"Fetched {len(display_data)} click activity records:")
                    st.table(display_data)
                else:
                    st.info("No click activity found for the given criteria.")
            except Exception as e:
                # Handle unexpected errors
                st.error(f"An error occurred while fetching click activity: {e}")
                st.write("Debug info:", e)  # Optional: Remove in production
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

with tab2:
    st.subheader("Fetch New Click Activity")

    # Fetch newsletters for the dropdown
    newsletters = fetch_all_newsletters()
    if not newsletters:
        st.error("No newsletters found in the database.")
    else:
        # Dropdown to select a newsletter
        list_id = st.selectbox(
            "Select a Newsletter:",
            options=[n["list_id"] for n in newsletters],
            format_func=lambda id: next((n["name"] for n in newsletters if n["list_id"] == id), id)
        )

        if st.button("Fetch Click Activity"):
            # Fetch subscribers for the selected newsletter
            subscribers = fetch_subscribers_sorted_by_clicks(list_id)

            if not subscribers:
                st.info("No subscribers found for this list.")
            else:
                # Initialize progress bar
                subscribers = sorted(subscribers, key=lambda s: s.get("total_clicks", 0), reverse=True)

                total_subscribers = len(subscribers)
                progress_bar = st.progress(0)

                # Fetch click activity for each subscriber
                processed_count = 0
                skipped_count = 0
                error_count = 0

                for idx, subscriber in enumerate(subscribers, start=1):
                    subscriber_hash = subscriber["subscriber_hash"]
                    activity = get_member_activity(list_id, subscriber_hash)

                    if not activity or "activity" not in activity:
                        print(f"No activity data for Subscriber {subscriber_hash}")
                        skipped_count += 1
                        continue

                    # Process click events
                    clicks = [act for act in activity["activity"] if act["action"] == "click"]
                    total_clicks = 0

                    for click in clicks:
                        slug = extract_slug_from_url(click.get("url", ""))
                        if not slug or slug == "unknown":
                            print(f"Skipped invalid slug for Subscriber {subscriber_hash}: {slug}")
                            skipped_count += 1
                            continue

                        post_details = get_post_details(slug, list_id)

                        if not post_details:
                            print(f"No headline available. Saving slug instead: {slug}.")
                            post_details = slug  # Fallback to slug if headline is not available
                            continue

                       
                        else: post_details = clean_headline(post_details) 

                         # Insert click activity into the database
                        try:
                            insert_click_activity(
                                subscriber_hash=subscriber_hash,
                                clicked_headline=post_details,
                                newsletter=list_id,
                                click_date=click["timestamp"]
                            )
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

                    # Update progress bar
                    progress_percentage = int((idx / total_subscribers) * 100)
                    progress_bar.progress(progress_percentage)

                # Display results
                st.success(f"Processed {processed_count} clicks.")
                st.warning(f"Skipped {skipped_count} invalid or duplicate clicks.")
                st.error(f"Encountered {error_count} errors.")