from pydantic import BaseModel
from typing import Optional, Any
from beanie import Document
from datetime import datetime
from model import Todo


class TodoOutboxDTO(BaseModel):
    todo_id:    Optional[int]      = None
    notion_id:  Optional[str]      = None
    event_type: Optional[str]      = None
    user_id:    Optional[str]      = None
    token_jti:  Optional[str]      = None
    payload:    Optional[Todo] = None
    
class TodoOutbox(Document):
    '''MongoDB 저장용'''
    todo_id:    Optional[int]      = None
    notion_id:  Optional[str]      = None
    event_type: Optional[str]      = None
    processed:  Optional[bool]     = None
    user_id:    Optional[str]      = None
    token_jti:  Optional[str]      = None
    payload:    Optional[dict[str, Any]] = None  # ← 자유로운 구조
    created_at: Optional[datetime] = None
    
    class Settings:
        name = "todo_outbox"
        