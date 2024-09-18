import json
import datetime
import firebase_admin
from matplotlib.pylab import f
import streamlit as st
from streamlit_option_menu import option_menu
from firebase_admin import credentials, firestore


def initialize_firebase():
    global auth
    if not firebase_admin._apps:
        firebase_admin.initialize_app(auth)

firebase_credentials = json.loads(st.secrets["firebase"]["firebase_credentials"])
auth = credentials.Certificate(firebase_credentials)

initialize_firebase()
db = firestore.client()

st.set_page_config(page_title="Daily Kharcha")

def valid_inputs(**kwargs):
    print("Validating inputs")
    for key, value in kwargs.items():
        print(f"{key}: {value}")
    return True


def register_user(email, password, name):
    user = auth.create_user(email=email, password=password)
    user_ref = db.collection('users').document(user.uid)
    user_ref.set({
        'name': name,
        'email': email
    })
    st.success(f"User {user.email} registered successfully!")


def login_user(email, password):

    user = auth.sign_in_with_email_and_password(email, password)
    if not user:
        st.error("Invalid email or password.")
        return None
    
    user_ref = db.collection('users').document(user.uid)
    user_data = user_ref.get().to_dict()

    st.session_state['user_id'] = user.uid
    st.session_state['user_email'] = user.email
    st.session_state['user_name'] = user_data.get('name', user.email)
    
    st.success(f"Welcome {st.session_state['user_name']}")
    return user


nav_args = {
    "styles": {"menu-title": {"align-self": "center"}},
    "default_index": 0,
    "orientation": "horizontal"
}

# st.session_state['user_id'] = "1234"
# st.session_state.pop("user_id", None)

if "user_id" in st.session_state:
    nav_option = option_menu(
        "Daily Kharcha",
        ["Today's Expenses", "Previous Expenses"],
        icons=['calendar-date', 'clock-history'],
        menu_icon="house-door", 
        **nav_args)
else:
    nav_option = option_menu(
        "Account",
        ["Login", "Register"],
        icons=['box-arrow-in-right', 'person-plus'],
        menu_icon="person-circle",
        **nav_args)
    
    if nav_option == "Register":
        with st.form("registration_form"):
            st.write("<div style='text-align:center; font-size:2rem; font-weight:600;'>Create an account</div>", unsafe_allow_html=True)
            error_space = st.empty()
            col1, col2 = st.columns(2, gap="medium")
            st.write("")
            col3, col4 = st.columns(2, gap="medium")
            st.write("")
            st.write("")
            _, submit_col, _ = st.columns([0.35, 0.3, 0.35])
            with col1:
                name = st.text_input("Name", placeholder="Your Full Name")
            with col2:
                email = st.text_input("Email", placeholder="your-email@domain.com")
            with col3:
                password = st.text_input("Password", type="password", placeholder="Shh! It's a secret")
            with col4:
                conf_password = st.text_input("Confirm Password", type="password", placeholder="Whisper it again!")
            with submit_col:
                submit_button = st.form_submit_button("Register", type="primary", use_container_width=True)
            
            if submit_button:
                if valid_inputs(**{"name": name, "email": email, "password": password, "conf_password": conf_password}):
                    print("REGISTERING")
                    print(email, password, name)
                    # register_user(email, password, name)
                else:
                    error_space.error("Please enter valid details.")        

    elif nav_option == "Login":
        with st.form("login_form"):
            st.write("<div style='text-align:center; font-size:2rem; font-weight:600;'>Sign in</div>", unsafe_allow_html=True)
            _, email_col, _ = st.columns([0.2, 0.6, 0.2])
            _, password_col, _ = st.columns([0.2, 0.6, 0.2])
            st.write("")
            st.write("")
            _, submit_col, _ = st.columns([0.35, 0.3, 0.35])
            with email_col:
                email = st.text_input("Email", placeholder="your-email@domain.com")
            with password_col:
                password =st.text_input("Password", type="password", placeholder="Whisper it!")
            with submit_col:
                submit_button = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit_button:
                if valid_inputs(**{"email": email, "password": password}):
                    print("LOGGING IN")
                    print(email, password)
                    # login_user(email, password)
                else:
                    st.error("Please enter email and password.")
    else:
        st.error("Invalid option selected.")
