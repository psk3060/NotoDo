from pydantic import BaseModel

from beanie import Document
from datetime import datetime
from typing import Optional

class RefreshTokenLogDTO(BaseModel):
    user_id: str
    token_hash: str
    jti: str
    issued_at: datetime
    expires_at: datetime
    ip: str | None
    user_agent: str | None
    issued_type: str

class RefreshTokenLog(Document):
    user_id : str
    jti : str
    token_hash : str
    issued_at : datetime
    expires_at : datetime
    revoked : bool = False
    revoked_at : Optional[datetime] = None
    revoked_reason : Optional[str] = None
    ip : Optional[str] = None
    user_agent : Optional[str] = None
    issued_type : Optional[str] = None # password, social, refresh
    
    class Settings:
        name = "refresh_token_logs"