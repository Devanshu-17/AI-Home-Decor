import streamlit as st
from hashlib import sha256
from uuid import uuid4
from streamlit_extras.let_it_rain import rain
from streamlit_extras.switch_page_button import switch_page
import base64
import io
import requests
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
 



# Set page configuration
st.set_page_config(
    page_title="Avalanche",
    page_icon="🔮")



# Utility functions
def hash_password(password):
    # Hash a password string using SHA256
    return sha256(password.encode("utf-8")).hexdigest()

def get_session_state():
    # Get the session state for the current session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if st.session_state.session_id not in st.session_state:
        st.session_state[st.session_state.session_id] = {}
    return st.session_state[st.session_state.session_id]

def set_session_state(state):
    # Set the session state for the current session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if st.session_state.session_id not in st.session_state:
        st.session_state[st.session_state.session_id] = {}
    st.session_state[st.session_state.session_id] = state


def register():
    st.header("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if password == confirm_password:
            st.success("You have successfully registered.")
            st.balloons()
        else:
            st.error("Passwords do not match.")
            
def login():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == "test" and password == "123456":
            set_session_state({"is_logged_in": True, "username": username})
            st.success("Logged in as {}".format(username))
            #switch to color_chooser page
            switch_page("color_chooser")
        else:
            st.error("Incorrect username or password.")

def home():
    st.markdown("""
    # 🏠 AI House Decor System

    Welcome to the **AI House Decor System**, a revolutionary new way to decorate your home! Our system uses advanced artificial intelligence algorithms to suggest decor ideas that suit your taste and style. With just a few clicks, you can transform your home into a stylish and comfortable space that reflects your personality.

    ## ✨ Key Features

    1. **Personalized recommendations** based on your preferences
    2. **Easy-to-use interface** for quick and hassle-free decorating
    3. **Option to save** your favorite decor idea for later
    4. **Real-time visualization** of decor options in your home

    We believe that everyone deserves a beautiful and comfortable home, and our system makes it easier than ever to achieve that. *Try it out today and see the difference for yourself!*

    ### 🌟 Here's an example of the difference our system **aims** to make:
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.image("1.jpg", caption="Before", use_column_width=True)
    with col2:
        st.image("2.png", caption="After", use_column_width=True)

def logout():
    set_session_state({"is_logged_in": False, "username": None})
    st._rerun()

# Main App
def main():    
    menu = ["Home", "Login", "Register"]
    choice = st.sidebar.selectbox("Select an option", menu)
    
    # Check if the user is logged in
    session_state = get_session_state()
    is_logged_in = session_state.get("is_logged_in", False)
    username = session_state.get("username", None)

    # Create a logout button container if the user is logged in
    if is_logged_in:
        logout_container = st.sidebar.container()
        with logout_container:
            st.button("Logout", on_click=logout)
    
    # Show the appropriate page based on user selection
    if choice == "Home":
        home()
    elif choice == "Login":
        login()
    elif choice == "Register":
        register()
    elif is_logged_in:
        st.success(f"Logged in as {username}")

main()