from pydantic import BaseModel, Field

class LoginRequest(BaseModel) :
    userId : str = Field(..., min_length=1, max_length=50)
    encryptedPassword : str = Field(..., description="Base64 encoded RSA encrypted password")
    
    def __init__(self, userId, encryptedPassword)  -> None:
        super().__init__(userId = userId, encryptedPassword = encryptedPassword)
        