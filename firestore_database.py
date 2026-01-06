from datetime import datetime
import streamlit as st
from firebase_db import tenant_ref


def _auftraege_collection():
    """Collection-Referenz für Aufträge im aktuellen Tenant."""
    return tenant_ref().collection("auftraggeber")


def load_data():
    """Aufträge laden – immer nur innerhalb des eigenen Tenants."""
    user = st.session_state.get("user")
    if not user:
        return []

    auftraege_ref = _auftraege_collection()

    if user["role"] == "admin":
        docs = auftraege_ref.stream()
    else:
        docs = auftraege_ref.where("user_id", "==", user["id"]).stream()

    return [doc.to_dict() for doc in docs]


def add_auftraggeber(name, adresse, email, telefon, auftragsart):
    """Neuen Auftraggeber im aktuellen Tenant speichern."""
    user = st.session_state.get("user")
    if not user:
        return

    auftraege_ref = _auftraege_collection()

    # IDs tenant-intern bestimmen
    docs = auftraege_ref.stream()
    ids = []
    for d in docs:
        data = d.to_dict()
        if isinstance(data.get("id"), int):
            ids.append(data["id"])

    next_id = (max(ids) + 1) if ids else 1

    doc_ref = auftraege_ref.document(str(next_id))
    doc_ref.set({
        "id": next_id,
        "user_id": user["id"],
        "name": name,
        "adresse": adresse,
        "email": email,
        "telefon": telefon,
        "auftragsart": auftragsart,
        "status": "offen",
        "erledigt_am": None,
    })


def markiere_als_erledigt(auftrag_id):
    auftraege_ref = _auftraege_collection()
    doc_ref = auftraege_ref.document(str(auftrag_id))
    doc_ref.update({
        "status": "erledigt",
        "erledigt_am": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    })


def delete_auftraggeber(auftrag_id):
    auftraege_ref = _auftraege_collection()
    auftraege_ref.document(str(auftrag_id)).delete()


def get_erledigte_auftraege():
    """Erledigte Aufträge – tenant-intern nach Rolle gefiltert."""
    user = st.session_state.get("user")
    if not user:
        return []

    auftraege_ref = _auftraege_collection()

    if user["role"] == "admin":
        docs = auftraege_ref.where("status", "==", "erledigt").stream()
    else:
        docs = (
            auftraege_ref
            .where("status", "==", "erledigt")
            .where("user_id", "==", user["id"])
            .stream()
        )

    return [doc.to_dict() for doc in docs]
