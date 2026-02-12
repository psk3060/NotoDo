from pydantic import BaseModel, Field
from typing import Optional

class GenerateTokenResponse(BaseModel) :
    user_id : str = Field(..., description = "Member ID that received the key")
    access_token : Optional[str] = Field(..., description = "Access Token")
    refresh_token : Optional[str] = Field(..., description = "Refresh Token")