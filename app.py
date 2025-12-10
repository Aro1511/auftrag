import streamlit as st
from auftrag import (
    load_data,
    save_data,
    add_auftraggeber,
    markiere_als_erledigt,
    get_erledigte_auftraege,
    delete_auftraggeber,
)

# Kopfzeile mit Titel links und Logo rechts
col1, col2 = st.columns([4, 1])  # Verhältnis: mehr Platz für den Titel
with col1:
    st.title("verwalte deine Auftäge")
with col2:
    st.image("logo.png", width=120)  # Logo rechts oben, Breite anpassbar

# Funktion zum Laden der CSS-Datei (optional und robust)
def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass  # CSS ist optional

# CSS einbinden
local_css("style.css")

st.title("📋 Auftraggeber Verwaltung")

# Session-State
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "show_details" not in st.session_state:
    st.session_state.show_details = {}
if "show_erledigte" not in st.session_state:
    st.session_state.show_erledigte = False

# Abschnitt: Neuen Auftraggeber hinzufügen
st.header("Neuen Auftraggeber hinzufügen")

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
                st.success(f"Auftraggeber '{name}' wurde gespeichert!")
                st.session_state.show_form = False
                st.rerun()
            else:
                st.error("Bitte alle Felder ausfüllen!")

# Abschnitt: Vorhandene Auftraggeber
st.header("Vorhandene Auftraggeber")
data = load_data()

if data:
    # Optional: offene zuerst anzeigen
    data_sorted = sorted(data, key=lambda x: x.get("status") != "offen")

    for index, ag in enumerate(data_sorted, start=1):
        ag_id = ag.get("id")  # durch Migration garantiert int
        # Button zum Anzeigen/Verbergen der Details (eindeutiger Key)
        name_btn_key = f"name_btn_{ag_id}"
        if st.button(f"{ag_id}. {ag['name']} ({ag.get('status','offen')})", key=name_btn_key):
            st.session_state.show_details[ag_id] = not st.session_state.show_details.get(ag_id, False)
            st.rerun()

        # Details nur anzeigen, wenn toggled
        if st.session_state.show_details.get(ag_id, False):
            st.write(f"Adresse: {ag.get('adresse', '')}")
            st.write(f"E-Mail: {ag.get('email', '')}")
            st.write(f"Telefon: {ag.get('telefon', '')}")
            st.write(f"Auftragsart: {ag.get('auftragsart', '')}")
            st.write(f"Status: {ag.get('status', 'offen')}")

            cols = st.columns([1, 1, 2])

            # Button: Auftrag erledigen (nur wenn offen)
            if ag.get("status") == "offen":
                if cols[0].button("Erledigen", key=f"done_{ag_id}"):
                    markiere_als_erledigt(ag_id)
                    st.success(f"Auftrag von '{ag['name']}' wurde als erledigt markiert.")
                    st.rerun()

            # Button: Löschen
            if cols[1].button("Löschen", key=f"delete_{ag_id}"):
                delete_auftraggeber(ag_id)
                st.warning(f"Auftraggeber '{ag['name']}' wurde gelöscht.")
                st.session_state.show_details.pop(ag_id, None)
                st.rerun()

            st.write("---")
else:
    st.info("Noch keine Auftraggeber vorhanden.")

# Abschnitt: Erledigte Aufträge
st.header("Erledigte Aufträge")

toggle_text = "Erledigte Aufträge anzeigen" if not st.session_state.show_erledigte else "Erledigte Aufträge ausblenden"
if st.button(toggle_text, key="toggle_erledigte"):
    st.session_state.show_erledigte = not st.session_state.show_erledigte
    st.rerun()

if st.session_state.show_erledigte:
    erledigte = get_erledigte_auftraege()
    if erledigte:
        for e in erledigte:
            st.write(f"{e['id']}. {e['name']} – {e['auftragsart']} (Status: {e['status']})")
    else:
        st.info("Noch keine erledigten Aufträge vorhanden.")
