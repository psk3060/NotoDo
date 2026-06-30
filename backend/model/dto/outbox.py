from pydantic import BaseModel
from typing import Optional, Any

class OutboxDTO(BaseModel):
    db_id : Optional[int] = None
    # 이벤트 호출자(sync_task, condition_task)
    event_caller : Optional[str]      = None
    parent_id : Optional[str]      = None
    child_id : Optional[str]      = None
    event_type: Optional[str]      = None
    user_id:    Optional[str]      = None
    token_jti:  Optional[str]      = None
    payload:    Optional[dict[str, Any]] = None