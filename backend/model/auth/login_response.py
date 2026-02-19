from pydantic import BaseModel
from typing import Optional

class LoginResponse(BaseModel) :
    success:bool
    message: Optional[str] = None