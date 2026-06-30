from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel) :
    userId : str = Field(..., min_length=1, max_length=50, description="회원ID")
    
    encryptedPassword: Optional[str] = Field(..., description="암호화된 패스워드")
    
    encryptedAESKey :  Optional[str] = Field(None, description="AES Key")
    
    iv: Optional[str] = Field(None, description="AES IV (Base64)")
    
class PublicKeyResponse(BaseModel):
    publicKey: str = Field(..., description="공개키")
    

class LoginResponse(BaseModel) :
    success : bool = Field(..., description="로그인 성공 여부")
    message: Optional[str] = Field(None, description="로그인 결과 메시지")