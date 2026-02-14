from pydantic import BaseModel, Field


class PublicKeyResponse(BaseModel):
    publicKey: str = Field(...)