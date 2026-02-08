from pydantic import BaseModel
from security.password import verify_password
from db.mongo import User

class AuthServiceImpl(BaseModel) : 
    
    async def login(self, userId:str, password:str) -> bool:
        # TODO IP에서 5회 실패 시 5분 잠금(Redis에서 카운트)
        
        # MongoDB
        user = await User.find_one(User.userId == userId)
        
        result = verify_password(password, user.password)
        
        return result