from datetime import datetime
from firebase_db import db
from utils import hash_password


TENANTS_COLLECTION = "tenants"


def list_tenants():
    """Alle Tenants (Kunden) auflisten."""
    docs = db.collection(TENANTS_COLLECTION).stream()
    tenants = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  # tenant_id
        tenants.append(data)
    return tenants


def create_tenant(tenant_id: str, name: str, admin_username: str, admin_password: str):
    """
    Neuen Tenant anlegen + initialen Admin-Benutzer erstellen.
    Struktur:
        tenants/<tenant_id>
            meta: name, active, created_at
            users/<admin_user>
    """
    tenant_id = tenant_id.strip()
    if not tenant_id:
        raise ValueError("Tenant-ID darf nicht leer sein.")

    tenant_doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    if tenant_doc_ref.get().exists:
        raise ValueError("Tenant-ID existiert bereits.")

    # Tenant-Metadaten
    tenant_doc_ref.set({
        "name": name,
        "active": True,
        "created_at": datetime.now()
    })

    # Initialer Admin-User im Tenant
    users_ref = tenant_doc_ref.collection("users")

    # Prüfen, ob Admin-Username im Tenant schon existiert
    existing = users_ref.where("username", "==", admin_username).limit(1).stream()
    if any(existing):
        raise ValueError("Admin-Benutzername im Tenant existiert bereits.")

    password_hash = hash_password(admin_password)
    admin_doc = users_ref.document()
    admin_doc.set({
        "username": admin_username,
        "password_hash": password_hash,
        "role": "admin",
        "created_at": datetime.now()
    })


def set_tenant_active(tenant_id: str, active: bool):
    """Tenant aktiv/inaktiv setzen."""
    tenant_doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    if not tenant_doc_ref.get().exists:
        raise ValueError("Tenant existiert nicht.")
    tenant_doc_ref.update({"active": active})


def delete_tenant(tenant_id: str):
    """
    Tenant-Dokument löschen.
    Achtung: Subcollections bleiben in Firestore bestehen, werden aber nicht mehr genutzt.
    Für vollständiges Löschen wäre ein rekursiver Delete nötig.
    """
    tenant_doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    if not tenant_doc_ref.get().exists:
        raise ValueError("Tenant existiert nicht.")
    tenant_doc_ref.delete()
