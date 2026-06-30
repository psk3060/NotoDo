from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RefreshTokenLogDTO(BaseModel):
    user_id: Optional[str] = None
    refresh_token_jti: Optional[str] = None
    refresh_token_hash: Optional[str] = None
    access_token_jti : Optional[str] = None
    access_token_hash : Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    issued_type: Optional[str] = None