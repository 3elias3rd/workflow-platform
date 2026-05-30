from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256


pwd_context = CryptContext(schemes=["bycrypt"])

def hash_password(plain: str) -> str:
    return pbkdf2_sha256.hash(plain)