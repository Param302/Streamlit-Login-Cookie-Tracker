import datetime
import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore

# Initialize Firebase
auth = credentials.Certificate("./firebase_credentials.json")
firebase_admin.initialize_app(auth)

# Connect to Firestore
db = firestore.client()