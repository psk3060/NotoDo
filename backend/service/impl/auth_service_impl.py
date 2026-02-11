from pydantic import BaseModel
from core.security import verify_password
from db.mongo import User

class AuthServiceImpl(BaseModel) : 
    
    # Login Check
    async def login(self, userId:str, password:str) -> bool:
        user = await User.find_one(User.userId == userId)
        
        if not user:
            raise ValueError("User not found in DB")
        
        result = verify_password(password, user.password)
        
        return result