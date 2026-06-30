from beanie import Document
from datetime import datetime
from typing import Optional

class RefreshTokenLogDocument(Document):
    user_id : Optional[str] = None
    refresh_token_jti : Optional[str] = None
    refresh_token_hash : Optional[str] = None
    access_token_jti : Optional[str] = None
    access_token_hash : Optional[str] = None
    issued_at : Optional[datetime] = None
    expires_at : Optional[datetime] = None
    revoked : Optional[bool] = False
    revoked_at : Optional[datetime] = None
    revoked_reason : Optional[str] = None
    ip : Optional[str] = None
    user_agent : Optional[str] = None
    issued_type : Optional[str] = None # password, social, refresh
    
    class Settings:
        name = "refresh_token_logs"