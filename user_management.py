from firebase_db import db
from utils import hash_password


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
    return user_data


def delete_user(user_id: str):
    """Nutzer löschen."""
    db.collection(USERS_COLLECTION).document(user_id).delete()
