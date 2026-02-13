from pydantic import BaseModel
from typing import Optional

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[str] = None
    description: Optional[str] = None 
    userId : Optional[str] = None 