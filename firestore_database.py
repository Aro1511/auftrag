from datetime import datetime
from firebase_db import db
import streamlit as st

COLLECTION = "auftraggeber"


def load_data():
    """Aufträge laden – Nutzer sieht eigene, Admin sieht alle."""
    user = st.session_state.get("user")
    if not user:
        return []

    if user["role"] == "admin":
        docs = db.collection(COLLECTION).stream()
    else:
        docs = db.collection(COLLECTION).where("user_id", "==", user["id"]).stream()

    return [doc.to_dict() for doc in docs]


def add_auftraggeber(name, adresse, email, telefon, auftragsart):
    """Neuen Auftraggeber für aktuellen Nutzer speichern."""
    user = st.session_state.get("user")
    if not user:
        return

    # IDs aus allen Aufträgen (global) bestimmen
    docs = db.collection(COLLECTION).stream()
    ids = []
    for d in docs:
        data = d.to_dict()
        if isinstance(data.get("id"), int):
            ids.append(data["id"])

    next_id = (max(ids) + 1) if ids else 1

    doc_ref = db.collection(COLLECTION).document(str(next_id))
    doc_ref.set({
        "id": next_id,
        "user_id": user["id"],  # Zuordnung zum Nutzer
        "name": name,
        "adresse": adresse,
        "email": email,
        "telefon": telefon,
        "auftragsart": auftragsart,
        "status": "offen",
        "erledigt_am": None,
    })


def markiere_als_erledigt(auftrag_id):
    doc_ref = db.collection(COLLECTION).document(str(auftrag_id))
    doc_ref.update({
        "status": "erledigt",
        "erledigt_am": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    })


def delete_auftraggeber(auftrag_id):
    db.collection(COLLECTION).document(str(auftrag_id)).delete()


def get_erledigte_auftraege():
    """Erledigte Aufträge – wieder nach Rolle filtern."""
    user = st.session_state.get("user")
    if not user:
        return []

    if user["role"] == "admin":
        docs = db.collection(COLLECTION).where("status", "==", "erledigt").stream()
    else:
        docs = (
            db.collection(COLLECTION)
            .where("status", "==", "erledigt")
            .where("user_id", "==", user["id"])
            .stream()
        )

    return [doc.to_dict() for doc in docs]
