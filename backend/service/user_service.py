from abc import ABC, abstractmethod

from repository import UserBaseRepository
from model import UserInfo

class UserService(ABC):
    
    @abstractmethod
    def find_by_id(userId : str):
        pass
    

class UserServiceImpl(UserService):
    
    def __init__(self, user_repository : UserBaseRepository):
        self.user_repository = user_repository
    
    async def find_by_id(self, userId : str) -> UserInfo | None:
        return await self.user_repository.find_by_id(userId)
    
    