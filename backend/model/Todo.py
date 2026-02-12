from pydantic import BaseModel
from typing import Optional

class Todo(BaseModel):
    id:int
    title: Optional[str] = None
    status: Optional[str] = None
    registDate:Optional[str] = None
    deadline:Optional[str] = None
    description: Optional[str] = None
