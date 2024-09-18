import datetime
import firebase_admin
import streamlit as st
from streamlit_option_menu import option_menu
from firebase_admin import credentials, firestore

# Initialize Firebase only if it has not been initialized
auth = credentials.Certificate("./firebase_credentials.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(auth)

# Connect to Firestore
db = firestore.client()

# Set up Streamlit page configuration
st.set_page_config(page_title="Daily Kharcha")

# st.session_state['user_id'] = "1234"
st.session_state.pop("user_id", None)

if "user_id" in st.session_state:
    nav_option = option_menu(
        "Daily Kharcha",
        ["Today's Expenses", "Previous Expenses"],
        icons=['calendar-date', 'clock-history'],
        styles={"menu-title": {"align-self": "center"}},
        menu_icon="house-door", 
        default_index=0, 
        orientation="horizontal")
else:
    nav_option = option_menu(
        "Account",
        ["Login", "Register"],
        icons=['box-arrow-in-right', 'person-plus'],
        styles={"menu-title": {"align-self": "center"}},
        menu_icon="person-circle", 
        default_index=0, 
        orientation="horizontal")
