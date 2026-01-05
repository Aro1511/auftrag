import hashlib


def hash_password(password: str) -> str:
    """Erzeugt einen SHA-256 Hash aus dem Passwort."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def check_password(password: str, password_hash: str) -> bool:
    """Vergleicht Klartext-Passwort mit gespeichertem Hash."""
    return hash_password(password) == password_hash
