from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    """Erzeugt einen bcrypt-Hash aus dem Passwort (über passlib)."""
    return bcrypt.hash(password)

def check_password(password: str, password_hash: str) -> bool:
    """Vergleicht Klartext-Passwort mit gespeichertem bcrypt-Hash."""
    return bcrypt.verify(password, password_hash)
