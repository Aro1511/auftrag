import streamlit as st
from google.cloud import firestore


@st.cache_resource
def get_db():
    """Initialisiert Firestore nur einmal (Streamlit-optimiert)."""
    return firestore.Client()


# Globale Firestore-Instanz
db = get_db()


def tenant_ref():
    """
    Gibt die Firestore-Referenz des aktuellen Tenants (Mandanten) zurück.
    Struktur: tenants/<tenant_id>
    """
    tenant_id = st.session_state.get("tenant_id")

    if not tenant_id:
        raise ValueError("Kein tenant_id in Session gefunden. Bitte Kunden-ID beim Login angeben.")

    return db.collection("tenants").document(tenant_id)
