from beanie import Document
from typing import Optional, Any
from datetime import datetime

class OutboxDocument(Document):
    '''outbox event - Save MongoDB'''
    db_id : Optional[int] = None
    # 이벤트 호출자(sync_task, condition_task)
    event_caller : Optional[str]      = None
    parent_id : Optional[str]      = None
    child_id : Optional[str]      = None
    event_type: Optional[str]      = None
    processed:  Optional[bool]     = None
    user_id:    Optional[str]      = None
    token_jti:  Optional[str]      = None
    payload:    Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Settings:
        name = "outbox"