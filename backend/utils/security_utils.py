from passlib.context import CryptContext
from passlib.exc import UnknownHashError

# Password 체크
bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# Password 암호화(테스트용으로만 사용)
def get_password_hash(password:str) -> str:
    return bcrypt_context.hash(password)

# plain_password : 입력 Password, User 테이블에 보관된 Password
def verify_password(input_password:str, hashed_password:str) -> bool:
    
    isPass = False
    
    try:
        isPass = bcrypt_context.verify(input_password, hashed_password)
    except UnknownHashError:
        isPass = False
        
    return isPass
    
# End Password 체크