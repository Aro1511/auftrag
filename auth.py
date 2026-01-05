import streamlit as st
from firebase_db import db
from user_management import get_user_by_username, create_user, list_users
from utils import check_password


def _has_any_user():
    """Prüfen, ob es bereits Nutzer gibt."""
    users = list_users()
    return len(users) > 0


def _create_initial_admin():
    st.title("👑 Ersten Admin anlegen")

    st.info("Es wurde noch kein Benutzer gefunden. Lege jetzt den ersten Admin-Zugang an.")

    username = st.text_input("Admin Benutzername")
    password = st.text_input("Admin Passwort", type="password")
    password_confirm = st.text_input("Passwort wiederholen", type="password")

    if st.button("Admin anlegen"):
        if not username or not password or not password_confirm:
            st.error("Bitte alle Felder ausfüllen.")
            return

        if password != password_confirm:
            st.error("Passwörter stimmen nicht überein.")
            return

        try:
            user = create_user(username, password, role="admin")
            st.success(f"Admin '{user['username']}' wurde angelegt. Du kannst dich jetzt einloggen.")
            st.session_state["setup_done"] = True
            st.rerun()
        except ValueError as e:
            st.error(str(e))


def show_login():
    """Login-UI anzeigen und Session setzen."""
    # Falls noch keine Nutzer existieren → Setup für ersten Admin
    if not _has_any_user() and not st.session_state.get("setup_done"):
        _create_initial_admin()
        return

    st.title("🔐 Login")

    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    if st.button("Login"):
        user = get_user_by_username(username)
        if not user:
            st.error("Benutzer existiert nicht.")
            return

        if not check_password(password, user["password_hash"]):
            st.error("Falsches Passwort.")
            return

        # User in Session speichern
        st.session_state["user"] = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
        }
        st.success(f"Willkommen, {user['username']}!")
        st.rerun()


def logout():
    """User ausloggen."""
    if "user" in st.session_state:
        del st.session_state["user"]
    st.rerun()
