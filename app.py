import streamlit as st
from firestore_database import (
    load_data,
    add_auftraggeber,
    markiere_als_erledigt,
    get_erledigte_auftraege,
    delete_auftraggeber,
)
from auth import show_login, logout
from user_management import list_users, create_user, delete_user
from logging_service import log_action
from firebase_db import db
import pandas as pd


def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass


def show_auftraege_seite():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Verwalte deine Aufträge")
    with col2:
        try:
            st.image("logo.png", width=120)
        except Exception:
            pass

    local_css("style.css")

    st.header("Neuen Auftraggeber hinzufügen")

    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    if "show_details" not in st.session_state:
        st.session_state.show_details = {}
    if "show_erledigte" not in st.session_state:
        st.session_state.show_erledigte = False

    if st.button("Einfügen", key="btn_einfuegen"):
        st.session_state.show_form = True

    if st.session_state.show_form:
        with st.form("auftraggeber_form"):
            name = st.text_input("Name")
            adresse = st.text_input("Adresse")
            email = st.text_input("E-Mail")
            telefon = st.text_input("Telefon")
            auftragsart = st.text_input("Auftragsart")

            submitted = st.form_submit_button("Speichern")

            if submitted:
                if all([name, adresse, email, telefon, auftragsart]):
                    add_auftraggeber(name, adresse, email, telefon, auftragsart)

                    log_action(
                        user=st.session_state["user"]["username"],
                        action="auftrag erstellt",
                        details=f"name: {name}"
                    )

                    st.success(f"Auftraggeber '{name}' wurde gespeichert!")
                    st.session_state.show_form = False
                    st.rerun()
                else:
                    st.error("Bitte alle Felder ausfüllen!")

    st.header("Vorhandene Auftraggeber")
    data = load_data()

    if data:
        data_sorted = sorted(data, key=lambda x: x.get("status") != "offen")

        for ag in data_sorted:
            ag_id = ag.get("id")
            name_btn_key = f"name_btn_{ag_id}"

            if st.button(
                f"{ag_id}. {ag['name']} ({ag.get('status','offen')})",
                key=name_btn_key,
            ):
                st.session_state.show_details[ag_id] = not st.session_state.show_details.get(ag_id, False)
                st.rerun()

            if st.session_state.show_details.get(ag_id, False):
                st.write(f"Adresse: {ag.get('adresse', '')}")
                st.write(f"E-Mail: {ag.get('email', '')}")
                st.write(f"Telefon: {ag.get('telefon', '')}")
                st.write(f"Auftragsart: {ag.get('auftragsart', '')}")
                st.write(f"Status: {ag.get('status', 'offen')}")

                if ag.get("status") == "erledigt":
                    st.write(f"➡️ wurde am {ag.get('erledigt_am', 'kein Datum gespeichert')} erledigt")

                cols = st.columns([1, 1, 2])

                if ag.get("status") == "offen":
                    if cols[0].button("Erledigen", key=f"done_{ag_id}"):
                        markiere_als_erledigt(ag_id)

                        log_action(
                            user=st.session_state["user"]["username"],
                            action="auftrag erledigt",
                            details=f"ID {ag_id}"
                        )

                        st.success(f"Auftrag von '{ag['name']}' wurde als erledigt markiert.")
                        st.rerun()

                if cols[1].button("Löschen", key=f"delete_{ag_id}"):
                    delete_auftraggeber(ag_id)

                    log_action(
                        user=st.session_state["user"]["username"],
                        action="auftrag gelöscht",
                        details=f"ID {ag_id}"
                    )

                    st.warning(f"Auftraggeber '{ag['name']}' wurde gelöscht.")
                    st.session_state.show_details.pop(ag_id, None)
                    st.rerun()

                st.write("---")
    else:
        st.info("Noch keine Auftraggeber vorhanden.")

    st.header("Erledigte Aufträge")

    toggle_text = (
        "Erledigte Aufträge anzeigen"
        if not st.session_state.show_erledigte
        else "Erledigte Aufträge ausblenden"
    )

    if st.button(toggle_text, key="toggle_erledigte"):
        st.session_state.show_erledigte = not st.session_state.show_erledigte
        st.rerun()

    if st.session_state.show_erledigte:
        erledigte = get_erledigte_auftraege()
        if erledigte:
            for e in erledigte:
                datum = e.get("erledigt_am", "kein Datum gespeichert")
                st.write(f"{e['id']}. {e['name']} – {e['auftragsart']} (Status: {e['status']})")
                st.write(f"➡️ wurde am {datum} erledigt")
                st.write("---")
        else:
            st.info("Noch keine erledigten Aufträge vorhanden.")


def show_admin_seite():
    st.title("👑 Admin – Benutzerverwaltung")

    st.subheader("Bestehende Benutzer")

    users = list_users()
    if not users:
        st.info("Noch keine Benutzer vorhanden.")
    else:
        for u in users:
            cols = st.columns([3, 2, 1])
            cols[0].write(f"**{u['username']}**")
            cols[1].write(f"Rolle: {u.get('role', 'user')}")

            current_user = st.session_state.get("user")
            if current_user and current_user["id"] == u["id"]:
                cols[2].write("Aktuell eingeloggt")
            else:
                if cols[2].button("Löschen", key=f"del_user_{u['id']}"):
                    delete_user(u["id"])

                    log_action(
                        user=st.session_state["user"]["username"],
                        action="benutzer gelöscht",
                        details=f"username: {u['username']}"
                    )

                    st.warning(f"Benutzer '{u['username']}' wurde gelöscht.")
                    st.rerun()

    st.subheader("Neuen Benutzer anlegen")

    new_username = st.text_input("Neuer Benutzername")
    new_password = st.text_input("Neues Passwort", type="password")
    role = st.selectbox("Rolle", ["user", "admin"])

    if st.button("Benutzer anlegen"):
        if not new_username or not new_password:
            st.error("Bitte Benutzername und Passwort eingeben.")
        else:
            try:
                create_user(new_username, new_password, role=role)

                log_action(
                    user=st.session_state["user"]["username"],
                    action="benutzer angelegt",
                    details=f"username: {new_username}"
                )

                st.success(f"Benutzer '{new_username}' wurde als {role} angelegt.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.subheader("📜 Aktivitätsprotokoll (Audit Log)")

    logs_ref = db.collection("logs").order_by("timestamp", direction="DESCENDING").stream()
    logs_list = []

    for log in logs_ref:
        entry = log.to_dict()
        entry["id"] = log.id
        logs_list.append(entry)

    if logs_list:
        df = pd.DataFrame(logs_list)

        st.dataframe(df, use_container_width=True)

        st.markdown("---")

        st.write("### Einzelne Log-Einträge löschen")

        for log in logs_list:
            cols = st.columns([6, 1])
            cols[0].write(
                f"**{log['timestamp']}** – {log['user']} – {log['action']} – {log.get('details','')}"
            )
            if cols[1].button("❌", key=f"delete_log_{log['id']}"):
                db.collection("logs").document(log["id"]).delete()

                log_action(
                    user=st.session_state["user"]["username"],
                    action="log-eintrag gelöscht",
                    details=f"log_id: {log['id']}"
                )

                st.warning("Ein Log-Eintrag wurde gelöscht.")
                st.rerun()

        st.markdown("---")

        if st.button("⚠️ Gesamtes Aktivitätsprotokoll löschen"):
            for log in logs_list:
                db.collection("logs").document(log["id"]).delete()

            log_action(
                user=st.session_state["user"]["username"],
                action="audit-log gelöscht",
                details="komplettes Log entfernt"
            )

            st.warning("Das gesamte Aktivitätsprotokoll wurde gelöscht.")
            st.rerun()

    else:
        st.info("Noch keine Log-Einträge vorhanden.")


def main():
    st.set_page_config(page_title="Auftragsverwaltung", page_icon="📋", layout="wide")

    if "user" not in st.session_state:
        show_login()
        return

    user = st.session_state["user"]

    with st.sidebar:
        st.markdown(f"**Eingeloggt als:** {user['username']}")
        st.markdown(f"**Rolle:** {user['role']}")

        if st.button("Logout"):
            logout()

        st.markdown("---")
        pages = ["Aufträge"]
        if user["role"] == "admin":
            pages.append("Admin")

        choice = st.radio("Navigation", pages)

    if choice == "Aufträge":
        show_auftraege_seite()
    elif choice == "Admin" and user["role"] == "admin":
        show_admin_seite()


if __name__ == "__main__":
    main()
