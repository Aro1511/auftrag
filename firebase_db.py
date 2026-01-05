import streamlit as st
from google.cloud import firestore

@st.cache_resource
def get_db():
    # Firestore-Zugangsdaten aus Streamlit Cloud Secrets
    key_dict = st.secrets["firestore"]
    return firestore.Client.from_service_account_info(key_dict)

db = get_db()
