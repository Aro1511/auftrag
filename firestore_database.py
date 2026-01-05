from datetime import datetime
from firebase_db import db

COLLECTION = "auftraggeber"

def load_data():
    docs = db.collection(COLLECTION).stream()
    return [doc.to_dict() for doc in docs]

def add_auftraggeber(name, adresse, email, telefon, auftragsart):
    daten = load_data()
    ids = [d["id"] for d in daten if isinstance(d.get("id"), int)]
    next_id = (max(ids) + 1) if ids else 1

    doc_ref = db.collection(COLLECTION).document(str(next_id))
    doc_ref.set({
        "id": next_id,
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
    docs = db.collection(COLLECTION).where("status", "==", "erledigt").stream()
    return [doc.to_dict() for doc in docs]
