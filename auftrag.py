import json
import os

# Pfad zur JSON-Datei
JSON_PATH = r"C:\Users\alrah\Desktop\auftrag\auftraggeber.json"

def load_data():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_auftraggeber(name, adresse, email, telefon, auftragsart):
    daten = load_data()

    neuer_auftraggeber = {
        "name": name,
        "adresse": adresse,
        "email": email,
        "telefon": telefon,
        "auftragsart": auftragsart
    }
    daten.append(neuer_auftraggeber)

    save_data(daten)
    print(f"Auftraggeber '{name}' wurde gespeichert.")
