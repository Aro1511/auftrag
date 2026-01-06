import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account

@st.cache_resource
def get_db():
    # Credentials aus Streamlit Secrets laden
    key_dict = st.secrets["firestore"]
    creds = service_account.Credentials.from_service_account_info(key_dict)

    # Firestore Client mit Credentials erstellen
    return firestore.Client(
        project=key_dict["project_id"],
        credentials=creds
    )

db = get_db()

def tenant_ref():
    tenant_id = st.session_state.get("tenant_id")
    if not tenant_id:
        raise ValueError("Kein tenant_id in Session gefunden.")
    return db.collection("tenants").document(tenant_id)
