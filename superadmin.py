import streamlit as st
from tenant_management import list_tenants, create_tenant, set_tenant_active, delete_tenant
from firebase_db import db


def show_superadmin_dashboard():
    st.title("🧩 Superadmin – Mandantenverwaltung")

    st.subheader("Neuen Mandanten anlegen")

    col1, col2 = st.columns(2)
    with col1:
        tenant_id = st.text_input("Tenant-ID (z. B. firma123)")
        tenant_name = st.text_input("Tenant-Name (Firmenname)")
    with col2:
        admin_username = st.text_input("Initialer Admin-Benutzername")
        admin_password = st.text_input("Initiales Admin-Passwort", type="password")

    if st.button("Mandanten anlegen"):
        if not all([tenant_id, tenant_name, admin_username, admin_password]):
            st.error("Bitte alle Felder ausfüllen.")
        else:
            try:
                create_tenant(tenant_id, tenant_name, admin_username, admin_password)
                st.success(f"Tenant '{tenant_id}' mit Admin '{admin_username}' wurde angelegt.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.markdown("---")
    st.subheader("Bestehende Mandanten")

    tenants = list_tenants()
    if not tenants:
        st.info("Noch keine Mandanten vorhanden.")
        return

    for t in tenants:
        cols = st.columns([3, 3, 2, 2, 2])
        cols[0].write(f"**Tenant-ID:** {t['id']}")
        cols[1].write(f"Name: {t.get('name', '-')}")
        cols[2].write(f"Aktiv: {t.get('active', True)}")

        # Aktiv/Passiv schalten
        if t.get("active", True):
            if cols[3].button("Deaktivieren", key=f"deact_{t['id']}"):
                set_tenant_active(t["id"], False)
                st.warning(f"Tenant '{t['id']}' wurde deaktiviert.")
                st.rerun()
        else:
            if cols[3].button("Aktivieren", key=f"act_{t['id']}"):
                set_tenant_active(t["id"], True)
                st.success(f"Tenant '{t['id']}' wurde aktiviert.")
                st.rerun()

        # Löschen
        if cols[4].button("Löschen", key=f"del_{t['id']}"):
            delete_tenant(t["id"])
            st.warning(f"Tenant '{t['id']}' wurde gelöscht.")
            st.rerun()

    st.markdown("---")
    st.subheader("Optional: Übersicht Superadmin-Log (global)")

    # Beispiel: globale Logs für Superadmin (falls du das später nutzt)
    if st.checkbox("Globale Superadmin-Logs anzeigen (falls vorhanden)"):
        logs_ref = db.collection("superadmin_logs").order_by("timestamp", direction="DESCENDING").limit(100).stream()
        for log in logs_ref:
            entry = log.to_dict()
            st.write(f"{entry.get('timestamp', '')} – {entry.get('user', '')} – {entry.get('action', '')}")
