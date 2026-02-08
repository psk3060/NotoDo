from passlib.context import CryptContext
from passlib.exc import UnknownHashError

# password.py

bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

def get_password_hash(password:str) -> str:
    return bcrypt_context.hash(password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    try :
        return bcrypt_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False

    