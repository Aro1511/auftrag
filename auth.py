import streamlit as st
from firebase_db import db
from user_management import get_user_by_username
from utils import check_password
from logging_service import log_action


# ---------------------------------------------------------
# AUTOMATISCHEN SUPERADMIN ERSTELLEN (LÖSUNG 2)
# ---------------------------------------------------------
def ensure_superadmin_exists():
    superadmin_id = "id1"
    username = "admin@abdi.de"

    # Neuer SHA-256 Hash für Passwort "inaosman"
    password_hash = "c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2"

    # Prüfen, ob superadmins/id1/users existiert
    users_ref = db.collection("superadmins").document(superadmin_id).collection("users")
    existing = list(users_ref.where("username", "==", username).limit(1).stream())

    if existing:
        return  # Superadmin existiert bereits

    # Superadmin automatisch erstellen
    users_ref.add({
        "username": username,
        "password_hash": password_hash,
        "role": "superadmin"
    })


# ---------------------------------------------------------
# MANDANTEN-LOGIN
# ---------------------------------------------------------
def _login_tenant():
    st.subheader("Mandanten-Login")

    tenant_id = st.text_input("Kunden-ID (Tenant-ID)")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    if st.button("Einloggen als Mandant"):
        if not tenant_id or not username or not password:
            st.error("Bitte alle Felder ausfüllen.")
            return

        # Tenant prüfen
        tenant_doc = db.collection("tenants").document(tenant_id).get()
        if not tenant_doc.exists:
            st.error("Unbekannte Kunden-ID (Tenant-ID).")
            return

        tenant_data = tenant_doc.to_dict()
        if not tenant_data.get("active", True):
            st.error("Dieser Mandant ist deaktiviert. Bitte Vermieter kontaktieren.")
            return

        # tenant_id in Session speichern
        st.session_state["tenant_id"] = tenant_id.strip()

        # Benutzer im entsprechenden Tenant suchen
        user = get_user_by_username(username)
        if not user:
            st.error("Benutzer existiert nicht.")
            return

        if not check_password(password, user["password_hash"]):
            st.error("Falsches Passwort.")
            return

        # Logging im Tenant
        log_action(
            user=username,
            action="login"
        )

        st.session_state["user"] = {
            "id": user["id"],
            "username": user["username"],
            "role": user.get("role", "user"),
            "type": "tenant",
        }
        st.success(f"Willkommen, {user['username']}!")
        st.rerun()


# ---------------------------------------------------------
# SUPERADMIN-LOGIN
# ---------------------------------------------------------
def _login_superadmin():
    st.subheader("Superadmin-Login")

    superadmin_id = st.text_input("Superadmin-ID")
    username = st.text_input("Superadmin-Benutzername")
    password = st.text_input("Superadmin-Passwort", type="password")

    if st.button("Einloggen als Superadmin"):
        if not superadmin_id or not username or not password:
            st.error("Bitte alle Felder ausfüllen.")
            return

        users_ref = db.collection("superadmins").document(superadmin_id).collection("users")
        query = users_ref.where("username", "==", username).limit(1).stream()

        admin_user = None
        for doc in query:
            data = doc.to_dict()
            data["id"] = doc.id
            admin_user = data
            break

        if not admin_user:
            st.error("Superadmin-Benutzer existiert nicht oder falsche Superadmin-ID.")
            return

        if not check_password(password, admin_user["password_hash"]):
            st.error("Falsches Passwort.")
            return

        st.session_state["user"] = {
            "id": admin_user["id"],
            "username": admin_user["username"],
            "role": "superadmin",
            "superadmin_id": superadmin_id,
            "type": "superadmin",
        }
        st.success(f"Superadmin '{admin_user['username']}' eingeloggt.")
        st.rerun()


# ---------------------------------------------------------
# LOGIN-SEITE
# ---------------------------------------------------------
def show_login():
    """Login-UI anzeigen und Session setzen."""
    st.title("🔐 Login")

    # AUTOMATISCHEN SUPERADMIN ERSTELLEN
    ensure_superadmin_exists()

    tab_tenant, tab_superadmin = st.tabs(["Mandant", "Superadmin"])

    with tab_tenant:
        _login_tenant()

    with tab_superadmin:
        _login_superadmin()


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
def logout():
    """User ausloggen."""
    if "user" in st.session_state:
        user = st.session_state["user"]
        if user.get("type") == "tenant":
            # Logging nur für Mandanten
            log_action(
                user=user["username"],
                action="logout"
            )
        del st.session_state["user"]

    if "tenant_id" in st.session_state:
        del st.session_state["tenant_id"]

    st.rerun()
