import streamlit as st
from auftrag import load_data, save_data, add_auftraggeber

st.title("📋 Auftraggeber Verwaltung")

# Session-State für Formularsteuerung
if "show_form" not in st.session_state:
    st.session_state.show_form = False

# Session-State für Details-Anzeige
if "show_details" not in st.session_state:
    st.session_state.show_details = {}

st.header("Neuen Auftraggeber hinzufügen")

# Button zum Anzeigen des Formulars
if st.button("Einfügen"):
    st.session_state.show_form = True

# Formular nur anzeigen, wenn show_form True ist
if st.session_state.show_form:
    with st.form("auftraggeber_form"):
        name = st.text_input("Name")
        adresse = st.text_input("Adresse")
        email = st.text_input("E-Mail")
        telefon = st.text_input("Telefon")
        auftragsart = st.text_input("Auftragsart")
        submitted = st.form_submit_button("Speichern")

        if submitted:
            if name and adresse and email and telefon and auftragsart:
                add_auftraggeber(name, adresse, email, telefon, auftragsart)
                st.success(f"Auftraggeber '{name}' wurde gespeichert!")
                # Formular wieder ausblenden
                st.session_state.show_form = False
                st.rerun()

            else:
                st.error("Bitte alle Felder ausfüllen!")

# Anzeige der vorhandenen Auftraggeber
st.header("Vorhandene Auftraggeber")
data = load_data()
if data:
    for idx, ag in enumerate(data, start=1):
        # Button für jeden Auftraggeber-Namen
        if st.button(f"{idx}. {ag['name']}", key=f"name_{idx}"):
            # Toggle Details-Anzeige
            st.session_state.show_details[idx] = not st.session_state.show_details.get(idx, False)
            st.rerun()


        # Details nur anzeigen, wenn show_details[idx] True ist
        if st.session_state.show_details.get(idx, False):
            st.write(f"Adresse: {ag['adresse']}")
            st.write(f"E-Mail: {ag['email']}")
            st.write(f"Telefon: {ag['telefon']}")
            st.write(f"Auftragsart: {ag['auftragsart']}")

            # Löschbutton für jeden Auftraggeber
            if st.button(f"Löschen {ag['name']}", key=f"delete_{idx}"):
                data.pop(idx - 1)
                save_data(data)
                st.warning(f"Auftraggeber '{ag['name']}' wurde gelöscht.")
                st.rerun()


            st.write("---")
else:
    st.info("Noch keine Auftraggeber vorhanden.")
