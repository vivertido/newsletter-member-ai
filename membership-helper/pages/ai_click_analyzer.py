import streamlit as st
from db import fetch_existing_clicks
import email_generator as gen

st.title("AI Click Analyzer")
st.markdown("Generate personalized marketing emails based on member click activity.")

# Input field for Subscriber Hash
subscriber_hash = st.text_input("Enter Subscriber Hash")


# Submit Button
if st.button("Generate Email"):
    if not subscriber_hash:
        st.error("Please enter a valid subscriber hash.")
    else:
        # Fetch existing clicks for the subscriber
        subscriber_clicks = fetch_existing_clicks(subscriber_hash)

        if not subscriber_clicks:
            st.warning("No click activity found for this subscriber.")
        else:
            # Show a spinner while generating the email
            with st.spinner(f"Analyzing click activity for subscriber: {subscriber_hash}"):
                generated_email = gen.generate_email(subscriber_clicks)

            # Display the generated email
            if generated_email:
                st.text_area("Generated Email", generated_email, height=600)
            else:
                st.error("Failed to generate email. Please try again.")




