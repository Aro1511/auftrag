from firebase_db import tenant_ref
from utils import hash_password


USERS_COLLECTION = "users"


def _users_collection():
    """Users-Collection im aktuellen Tenant."""
    return tenant_ref().collection(USERS_COLLECTION)


def get_user_by_username(username: str):
    """Hole einen Nutzer anhand des Usernamens (im aktuellen Tenant)."""
    users_ref = _users_collection()
    query = users_ref.where("username", "==", username).limit(1).stream()

    for doc in query:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    return None


def list_users():
    """Alle Nutzer im aktuellen Tenant auflisten."""
    users_ref = _users_collection()
    docs = users_ref.stream()
    users = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        users.append(data)

    return users


def create_user(username: str, password: str, role: str = "user"):
    """Neuen Nutzer im aktuellen Tenant anlegen."""
    users_ref = _users_collection()

    if get_user_by_username(username):
        raise ValueError("Benutzername existiert bereits.")

    password_hash = hash_password(password)

    doc_ref = users_ref.document()
    user_data = {
        "username": username,
        "password_hash": password_hash,
        "role": role,
    }
    doc_ref.set(user_data)

    user_data["id"] = doc_ref.id
    return user_data


def delete_user(user_id: str):
    """Nutzer im aktuellen Tenant löschen."""
    _users_collection().document(user_id).delete()
