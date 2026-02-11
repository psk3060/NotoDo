from pydantic import BaseModel

class PublicKeyResponse(BaseModel):
    publicKey: str