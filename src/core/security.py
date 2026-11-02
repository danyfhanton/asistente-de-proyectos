import hashlib
import os

SALT = "asistente_de_proyectos_salt_key_2026"


def hash_password(password: str) -> str:
    salted = f"{SALT}:{password}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

