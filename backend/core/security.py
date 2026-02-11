# core.security.py : 보안과 관련된 모든 요소

from fastapi import HTTPException
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from model.LoginRequest import LoginRequest

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


# RSA 키 페어 생성(공개키, 개인키)
class RSAKeyManager :
    def __init__(self):
        self._private_key = None
        self._public_key = None
    
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
    def export_public_key_pem(self) -> str:
        pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    # RSA로 암호화된 패스워드 복호화
    @DeprecationWarning
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
    
    # RSA Private Key로 AES 키 복호화 & AES-GCM으로 데이터 복호화
    def decrypt_password_AES(self, loginRequest:LoginRequest) -> str:
        
        try :
            encrypted_aes_key_bytes = base64.b64decode(loginRequest.encryptedAESKey)
            encrypted_data_bytes = base64.b64decode(loginRequest.encryptedPassword)
            iv_bytes = base64.b64decode(loginRequest.iv)
            
            # RSA Private key로 AES 키 복호화
            decryptedAESKey = self._private_key.decrypt(
                encrypted_aes_key_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            auth_tag = encrypted_data_bytes[-16:]
            ciphertext = encrypted_data_bytes[:-16]
            
            cipher = Cipher(
                algorithms.AES(decryptedAESKey),
                modes.GCM(iv_bytes, auth_tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            return decrypted_data.decode('utf-8')
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"복호화 실패 - 데이터 검증 오류: {str(e)}"
            )
        except Exception as e:
            
            raise HTTPException(
                status_code=999,
                detail=f"복호화 실패: {str(e)}"
            )
        

# 전역 변수(@asynccontextmanager에서 rsa_manager.init() 호출)
rsa_manager = RSAKeyManager()




# TODO JWT 토큰 생성
