import streamlit as st

# Load credentials from secrets
USERNAME = st.secrets["auth"]["username"]
PASSWORD = st.secrets["auth"]["password"]

def authenticate(username, password):
    """
    Authenticate the user with hard-coded credentials.

    Args:
        username (str): Entered username.
        password (str): Entered password.

    Returns:
        bool: True if authenticated, False otherwise.
    """
    return username == USERNAME and password == PASSWORD

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    

if not st.session_state["authenticated"]:
    # Display the login form
    st.title("Login")
    st.markdown("Enter your credentials to access the app.")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.success("Login successful!")
            st.session_state["authenticated"] = True
            
            # Redirect to the main app
            st.switch_page("app.py")
            #st.rerun()
        else:
            st.error("Invalid username or password.")
else:
    # Display logged-in status and logout button
    st.title("You are already logged in!")
    st.sidebar.write("Logged in!")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.sidebar.write("You have been logged out.")
        st.experimental_set_query_params(page="login")
        st.rerun()