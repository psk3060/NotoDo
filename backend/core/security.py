# core.security.py : 보안과 관련된 모든 요소
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64

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


# TODO RSA 키 페어 생성(공개키, 개인키)
class RSAKeyManager :
    def __init__(self):
        self._private_key = None
        self._public_key = None
        # self._generate_keys()
    
    def init(self) :
        if self._private_key is not None:
            return
        self._generate_keys()
    
    def _generate_keys(self) :
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self._public_key = self._private_key.public_key()
    
    # 공개키를 문자열로 반환
    def get_public_key_pem(self) -> str:
        pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    def public_key_fingerprint(self):
        der = self._public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        digest = hashes.Hash(hashes.SHA256())
        digest.update(der)
        return digest.finalize().hex()

    # 암호화된 패스워드 복호화
    def decrypt_password(self, encrypted_password_b64:str) -> str:
        
        try :
            # Base64 디코딩
            encrypted_bytes = base64.b64decode(encrypted_password_b64)
            
            # RSA 복호화
            decrypted_bytes = self._private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted_bytes.decode('utf-8')
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise ValueError("RSA decrypt failed")
    

# 전역 변수
rsa_manager = RSAKeyManager()



# TODO JWT 토큰 생성
