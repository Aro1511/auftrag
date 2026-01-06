from datetime import datetime
from firebase_db import tenant_ref


def log_action(user: str, action: str, details: str = ""):
    """
    Speichert eine Aktion im Log des aktuellen Tenants.
    Wenn kein tenant_id gesetzt ist (z.B. bei Superadmin), wird nichts geloggt.
    """
    try:
        logs_ref = tenant_ref().collection("logs")
    except ValueError:
        # Kein Tenant gesetzt – vermutlich Superadmin oder vor Login – nichts loggen
        return

    logs_ref.add({
        "user": user,
        "action": action,
        "details": details,
        "timestamp": datetime.now()
    })
