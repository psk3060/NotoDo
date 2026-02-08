from pydantic import BaseModel

class LoginParam(BaseModel) :
    userId : str
    password : str
    
    def __init__(self, userId, password)  -> None:
        super().__init__(userId = userId, password = password)
        self.userId = userId
        self.password = password