import streamlit as st


if not st.session_state.get("authenticated", False):
    st.error("You must log in to access this page.")
    st.stop()  # Stop further execution of the page

API_KEY = st.secrets["API_KEY"]
MC_KEY = st.secrets["MC_KEY"]
OPEN_AI_KEY =st.secrets["OPEN_AI_KEY"]

SERVER_PREFIX = 'us2'  # Replace 'usX' with your specific Mailchimp server prefix
BASE_URL = f'https://{SERVER_PREFIX}.api.mailchimp.com/3.0/'
HEADERS = {
    'Authorization': f'Bearer {MC_KEY}'
    }




st.title("Cityside Membership Helper")
st.write("Now with supabase!")