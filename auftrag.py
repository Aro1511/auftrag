import json
import os
from datetime import datetime

# relativer Pfad zur JSON-Datei
JSON_PATH = os.path.join(os.path.dirname(__file__), "auftraggeber.json")


def _ensure_file_exists():
    """Stellt sicher, dass die JSON-Datei existiert und eine leere Liste enthält."""
    folder = os.path.dirname(JSON_PATH)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(JSON_PATH):
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)


def load_data():
    """Lädt Daten und migriert fehlende Felder (id, status)."""
    _ensure_file_exists()
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except (json.JSONDecodeError, FileNotFoundError):
        data = []

    # Migration: fehlende id/status hinzufügen
    existing_ids = {item.get("id") for item in data if isinstance(item.get("id"), int)}
    next_id = (max(existing_ids) + 1) if existing_ids else 1

    changed = False
    for item in data:
        # id setzen, wenn fehlt oder ungültig
        if not isinstance(item.get("id"), int):
            item["id"] = next_id
            next_id += 1
            changed = True
        # status default setzen
        if item.get("status") not in ("offen", "erledigt"):
            item["status"] = "offen"
            changed = True

    if changed:
        save_data(data)

    return data


def save_data(data):
    _ensure_file_exists()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def _get_next_id(data):
    """Gibt eine neue eindeutige ID zurück."""
    ids = [item.get("id") for item in data if isinstance(item.get("id"), int)]
    return (max(ids) + 1) if ids else 1


def add_auftraggeber(name, adresse, email, telefon, auftragsart):
    daten = load_data()
    neuer_auftraggeber = {
        "id": _get_next_id(daten),
        "name": name,
        "adresse": adresse,
        "email": email,
        "telefon": telefon,
        "auftragsart": auftragsart,
        "status": "offen",
    }
    daten.append(neuer_auftraggeber)
    save_data(daten)


def markiere_als_erledigt(auftrag_id):
    """Setzt den Status eines Auftrags auf 'erledigt' und speichert Datum/Uhrzeit."""
    daten = load_data()
    updated = False
    for ag in daten:
        if ag.get("id") == auftrag_id:
            ag["status"] = "erledigt"
            ag["erledigt_am"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            updated = True
            break
    if updated:
        save_data(daten)


def get_erledigte_auftraege():
    """Gibt alle erledigten Aufträge zurück."""
    daten = load_data()
    return [ag for ag in daten if ag.get("status") == "erledigt"]


def delete_auftraggeber(auftrag_id):
    """Löscht einen Auftraggeber anhand seiner ID."""
    daten = load_data()
    new_data = [ag for ag in daten if ag.get("id") != auftrag_id]
    save_data(new_data)
