import hashlib
import bcrypt
import os
import binascii
from argon2 import PasswordHasher

# تهيئة Argon2
argon2_hasher = PasswordHasher()

def generate_hashes(password: str) -> dict:
    """
    توليد مجموعة من الـ Hashes باستخدام خوارزميات مختلفة
    """
    return {
        "MD5": hashlib.md5(password.encode()).hexdigest(),
        "SHA1": hashlib.sha1(password.encode()).hexdigest(),
        "SHA256": hashlib.sha256(password.encode()).hexdigest(),
        "SHA512": hashlib.sha512(password.encode()).hexdigest(),
        "bcrypt": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        "PBKDF2": binascii.hexlify(
            hashlib.pbkdf2_hmac("sha256", password.encode(), b"salt", 100000)
        ).decode(),
        "Argon2": argon2_hasher.hash(password)
    }