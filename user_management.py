from firebase_db import db
from utils import hash_password
from logging_service import log_action   # ← NEU: Logging importieren
import streamlit as st                   # ← NEU: Für Zugriff auf eingeloggten User


USERS_COLLECTION = "users"


def get_user_by_username(username: str):
    """Hole einen Nutzer anhand des Usernamens."""
    users_ref = db.collection(USERS_COLLECTION)
    query = users_ref.where("username", "==", username).limit(1).stream()

    for doc in query:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    return None


def list_users():
    """Alle Nutzer auflisten."""
    users_ref = db.collection(USERS_COLLECTION)
    docs = users_ref.stream()
    users = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        users.append(data)

    return users


def create_user(username: str, password: str, role: str = "user"):
    """Neuen Nutzer anlegen."""
    users_ref = db.collection(USERS_COLLECTION)

    # Prüfen, ob Username schon existiert
    if get_user_by_username(username):
        raise ValueError("Benutzername existiert bereits.")

    password_hash = hash_password(password)

    doc_ref = users_ref.document()
    user_data = {
        "username": username,
        "password_hash": password_hash,
        "role": role,  # "admin" oder "user"
    }
    doc_ref.set(user_data)

    user_data["id"] = doc_ref.id

    # Logging
    if "user" in st.session_state:
        log_action(
            user=st.session_state["user"]["username"],
            action="benutzer angelegt",
            details=f"username: {username}, role: {role}"
        )

    return user_data


def delete_user(user_id: str):
    """Nutzer löschen."""
    # Nutzer-Daten vorher holen (für Logging)
    user_doc = db.collection(USERS_COLLECTION).document(user_id).get()
    deleted_username = None

    if user_doc.exists:
        deleted_username = user_doc.to_dict().get("username", "unbekannt")

    # Löschen
    db.collection(USERS_COLLECTION).document(user_id).delete()

    # Logging
    if "user" in st.session_state:
        log_action(
            user=st.session_state["user"]["username"],
            action="benutzer gelöscht",
            details=f"username: {deleted_username}"
        )
