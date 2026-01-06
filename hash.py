from utils import hash_password

def main():
    # Hier trägst du dein gewünschtes Passwort ein
    password = "inaosman"
    hashed = hash_password(password)
    print("Generierter Passwort-Hash:")
    print(hashed)

if __name__ == "__main__":
    main()
