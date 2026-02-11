from pydantic import BaseModel

# TODO access_token, refresh_token
class LoginResponse(BaseModel) :
    success:bool
    message: str | None = None
    
    def __init__(self, success, message)  -> None:
        super().__init__(success = success, message = message)
        self.success = success
        self.message = message