# logging_service.py
from firebase_db import db
from datetime import datetime

def log_action(user, action, details=""):
    """Speichert eine Aktion im Firestore-Log."""
    db.collection("logs").add({
        "user": user,
        "action": action,
        "details": details,
        "timestamp": datetime.now()
    })
