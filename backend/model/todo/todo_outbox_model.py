from pydantic import BaseModel
from typing import Optional, Any
from beanie import Document
from datetime import datetime



class TodoCommentOutboxDTO(BaseModel):
    db_id : Optional[int] = None
    todo_id : Optional[str]      = None
    comment_id : Optional[str]      = None
    event_type: Optional[str]      = None
    user_id:    Optional[str]      = None
    token_jti:  Optional[str]      = None
    payload:    Optional[dict[str, Any]] = None


class TodoCommentOutbox(Document):
    '''outbox event - TodoComment(Save MongoDB)'''
    db_id : Optional[int] = None
    todo_id : Optional[str]      = None
    comment_id : Optional[str]      = None
    event_type: Optional[str]      = None
    processed:  Optional[bool]     = None
    user_id:    Optional[str]      = None
    token_jti:  Optional[str]      = None
    payload:    Optional[dict[str, Any]] = None
    try_cnt : Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Settings:
        name = "todo_comment_outbox"
    

class TodoOutboxDTO(BaseModel):
    db_id : Optional[int] = None
    todo_id:  Optional[str]      = None
    event_type: Optional[str]      = None
    user_id:    Optional[str]      = None
    token_jti:  Optional[str]      = None
    payload:    Optional[dict[str, Any]] = None
    
class TodoOutbox(Document):
    '''outbox event - Todo(Save MongoDB)'''
    db_id : Optional[int] = None
    todo_id:  Optional[str]      = None
    event_type: Optional[str]      = None
    processed:  Optional[bool]     = None
    user_id:    Optional[str]      = None
    token_jti:  Optional[str]      = None
    payload:    Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Settings:
        name = "todo_outbox"
        