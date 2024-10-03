import re
import json
import time
import pyrebase
import firebase_admin
import streamlit as st
from datetime import timedelta, datetime
from requests.exceptions import HTTPError
from streamlit_option_menu import option_menu
from streamlit_js_eval import streamlit_js_eval
from extra_streamlit_components import CookieManager
from firebase_admin import credentials, firestore, auth as admin_auth


def initialize_firebase():
    firebase_credentials = json.loads(st.secrets["firebase"]["credentials"])
    firebase_config = json.loads(st.secrets["firebase"]["config"])

    cred = credentials.Certificate(firebase_credentials)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    return pyrebase.initialize_app(firebase_config)

firebase = initialize_firebase()
auth = firebase.auth()
db = firestore.client()

st.set_page_config(page_title="Daily Kharcha", page_icon="💰")

cookies = CookieManager()
cookie_params = {
    "expires_at": datetime.now() + timedelta(days=14),
    "secure": True
}

st.markdown(
    """<style>
        .element-container:has(iframe[height="0"]) { display: contents !important; }
    </style>""",
    unsafe_allow_html=True,
)

def reload_page():
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

def validate_inputs(**params) -> bool:  
    empty_values = [f"**{key.title()}**" for key, value in params.items() if not value]
    if empty_values:
        st.error(f"Please enter {(', '.join(empty_values[:-1]) + ' and ' + empty_values[-1]) if len(empty_values) > 1 else empty_values[0]}.")
        return False
    
    errors = []
    email = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$").match(params["email"].strip())  
    if not email:
        errors.append("Invalid email address.")
    else:
        email = email.group()
    
    # if sign in form
    if len(params) == 2:
        if errors:
            st.error("Please enter valid email address and password.")
            return False
        return True

    # if sign up form
    password = params["password"].strip()
    conf_password = params["confirm_password"].strip()
    name = params["name"].strip()

    if len(password) < 8 or len(password) > 32:
        errors.append("Password should be 8 to 32 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password should contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password should contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        errors.append("Password should contain at least one number.")
    if not re.search(r"[^\w\d]", password):
        errors.append("Password should contain at least one special character.")

    if name.lower() in password.lower():
        errors.append("Password should not contain your name.")

    if password != conf_password.strip():
        errors.append("Password and Confirm password do not match.")
    
    if errors:
        error_msg = "**Please fix the following errors:**\n\n"
        error_msg += "\n".join([f"- {error}" for error in errors])
        error_space.error(error_msg)

    return not errors

def start_registration_process(email, password, name) -> int:
    """
    This function will register, verify and update user profile.
    """
    with st.spinner("Registering..."):
        if register_user(email, password, name):
            return -1
        error_space.success("Registration successful!")
    verify_email(st.session_state.reg_user)
    verify_email_dialog(st.session_state.reg_user)
    return 0

def register_user(email, password, name) -> int:
    try:
        user = auth.create_user_with_email_and_password(email, password)
    except HTTPError:
        return -1
    else:
        auth.update_profile(user['idToken'], display_name=name)
        st.session_state.reg_user = user
        return 0

def verify_email(user):
    user = auth.refresh(user['refreshToken'])
    auth.send_email_verification(user['idToken'])


@st.dialog("Verify your Email")
def verify_email_dialog(user):

    def wrapper():
        st.session_state.email_resend = True
        verify_email(user)
        msg.info("Verification link has been resent. Please check your inbox.")
        st.stop()

    msg = st.empty()
    st.markdown("""Please verify your email to activate your account. A verification link has been sent to your inbox. 

Check your email (including spam/junk folders) and click the link to complete the process.""")
    
    
    if 'reg_user' in st.session_state:
        return

    _, resend, _ = st.columns(3)
    st.session_state.email_resend = False
    resend_btn = resend.button("Resend", type="primary", use_container_width=True, on_click=wrapper, disabled=st.session_state.email_resend)


def is_email_verified(user):
    details = auth.get_account_info(user['idToken'])
    return details['users'][0]['emailVerified']

def login_user_with_cookie():
    user = cookies.get("cookie_user")
    if not is_email_verified(user):
        verify_email_dialog(user)
        return

    st.session_state.user = user

    st.session_state.user = user
    try:
        auth.get_account_info(user['idToken'])
    except HTTPError:   # invalid token/token expired
        user = auth.refresh(user['refreshToken'])
    
        cookies.set("cookie_user", user, key="cookie_user", **cookie_params)
        cookies.set("cookie_user_details", cookies.get("cookie_user_details"), key="cookie_user_details", **cookie_params)
        auth.get_account_info(user['idToken'])

    st.session_state["user_details"] = cookies.get("cookie_user_details")


def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
    except HTTPError:
        status_space.error("Invalid email or password.")
        return
    
    if not is_email_verified(user):
        status_space.error("Email Not Verified!")
        verify_email_dialog(user)
        return

    cookies.set("cookie_user", user, key="cookie_user", **cookie_params)
    cookies.set("cookie_user_details", {
        "email": user["email"],
        "displayName": user['displayName']
    }, key="cookie_user_details", **cookie_params)

    st.session_state.user_details = cookies.get("cookie_user_details")

    status_space.success(f"Welcome **{st.session_state.user_details['displayName']}**!")
    time.sleep(2)
    reload_page()

def logout_user():
    try:
        st.session_state.pop("cookie_user")
        st.session_state.pop("cookie_user_details")
        st.session_state.pop("user_details")
    except KeyError:
        pass
    cookies.delete("cookie_user", key="cookie_user")
    cookies.delete("cookie_user_details", key="cookie_user_details")

    # st.rerun()
    reload_page()


nav_args = {
    "styles": {"menu-title": {"align-self": "center"}},
    "default_index": 0,
    "orientation": "horizontal"
}

if cookies.get("cookie_user") and cookies.get("cookie_user_details"):
    login_user_with_cookie()
    nav_option = option_menu(
        f"Daily Kharcha",
        ["Today's Expenses", "Previous Expenses"],
        icons=['calendar-date', 'clock-history'],
        menu_icon="person-circle", 
        **nav_args)
    
    if nav_option == "Today's Expenses":
        if st.button("Logout"):
            logout_user()
else:
    st.markdown("""<style>.stSpinner>div{display:flex;justify-content:center;}</style>""",
            unsafe_allow_html=True)
            
    nav_option = option_menu(
        "Daily Kharcha",
        ["Login", "Register"],
        icons=['box-arrow-in-right', 'person-plus'],
        menu_icon="person-circle",
        **nav_args)
    
    if nav_option == "Register":
        with st.form("registration_form", clear_on_submit=True):
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
                if validate_inputs(name=name, email=email, password=password, confirm_password=conf_password):
                # if True:
                    name = name.strip()
                    email = email.strip().lower()
                    password = password.strip()
                    conf_password = conf_password.strip()
                    response = start_registration_process(email, password, name)
                    if response == -1:
                        error_space.error(f"Email ID is already registered. Please login to continue.")
                    else:
                        user = admin_auth.get_user_by_email(email)
                        if user.email_verified:
                            error_space.success("You are verified! Please login to continue.")
                        else:
                            error_space.success("Registration successful! Please verify your email to activate your account.")
                    st.session_state.clear()

    elif nav_option == "Login":
        with st.form("login_form"):
            st.write("<div style='text-align:center; font-size:2rem; font-weight:600;'>Sign in</div>", unsafe_allow_html=True)
            status_space = st.empty()
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
                if validate_inputs(**{"email": email, "password": password}):
                    email = email.strip()
                    password = password.strip()
                    login_user(email, password)

