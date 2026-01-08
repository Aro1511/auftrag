import streamlit as st
from firebase_db import db
from user_management import get_user_by_username
from utils import check_password
from logging_service import log_action


# ---------------------------------------------------------
# AUTOMATISCHEN SUPERADMIN ERSTELLEN (NEUE VERSION)
# ---------------------------------------------------------
def ensure_superadmin_exists():
    superadmin_id = "id1"
    username = "admin@abdi.de"

    # SHA-256 Hash für Passwort "inaosman"
    password_hash = "f3efebc1866b910a6f87229ea365a64463c1377404d341e8587b397d4b5daf6c"

    # Fester Dokumentname, damit der Eintrag IMMER überschrieben wird
    users_ref = db.collection("superadmins").document(superadmin_id).collection("users")
    admin_doc_ref = users_ref.document("admin_user")

    # Superadmin immer setzen/überschreiben
    admin_doc_ref.set({
        "username": username,
        "password_hash": password_hash,
        "role": "superadmin",
    }, merge=True)


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

        tenant_doc = db.collection("tenants").document(tenant_id).get()
        if not tenant_doc.exists:
            st.error("Unbekannte Kunden-ID (Tenant-ID).")
            return

        tenant_data = tenant_doc.to_dict()
        if not tenant_data.get("active", True):
            st.error("Dieser Mandant ist deaktiviert.")
            return

        st.session_state["tenant_id"] = tenant_id.strip()

        user = get_user_by_username(username)
        if not user:
            st.error("Benutzer existiert nicht.")
            return

        if not check_password(password, user["password_hash"]):
            st.error("Falsches Passwort.")
            return

        log_action(user=username, action="login")

        st.session_state["user"] = {
            "id": user["id"],
            "username": user["username"],
            "role": user.get("role", "user"),
            "type": "tenant",
        }

        st.success(f"Willkommen, {user['username']}")
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
            st.error("Superadmin existiert nicht oder falsche ID.")
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

        st.success(f"Superadmin {admin_user['username']} eingeloggt.")
        st.rerun()


# ---------------------------------------------------------
# LOGIN-SEITE
# ---------------------------------------------------------
def show_login():
    st.title("Login")

    # Superadmin wird immer korrekt erstellt
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
    if "user" in st.session_state:
        user = st.session_state["user"]

        if user.get("type") == "tenant":
            log_action(user=user["username"], action="logout")

        del st.session_state["user"]

    if "tenant_id" in st.session_state:
        del st.session_state["tenant_id"]

    st.rerun()
