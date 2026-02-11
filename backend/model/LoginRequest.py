from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel) :
    userId : str = Field(..., min_length=1, max_length=50, description="회원ID")
    
    encryptedPassword: Optional[str] = Field(..., description="암호화된 패스워드")
    
    encryptedAESKey :  Optional[str] = None
    
    # AES IV (Base64)
    iv: Optional[str] = None
    