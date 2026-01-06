import bcrypt

def hash_password(password: str) -> str:
    """Erzeugt einen bcrypt-Hash aus dem Passwort."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(password: str, password_hash: str) -> bool:
    """Vergleicht Klartext-Passwort mit gespeichertem bcrypt-Hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
