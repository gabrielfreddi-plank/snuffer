import os
import hashlib
import base64

def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return base64.b64encode(dk).decode(), base64.b64encode(salt).decode()

def verify_password(password: str, hashed: str, salt: str) -> bool:
    salt_bytes = base64.b64decode(salt)
    computed, _ = hash_password(password, salt_bytes)
    return computed == hashed

if __name__ == "__main__":
    h, s = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", h, s)
    print("Password hashing OK")
