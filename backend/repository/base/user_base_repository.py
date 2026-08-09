from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from model import UserInfo

from repository.base.base_repository import BaseRepository

class UserBaseRepository(BaseRepository):
    def __init__(self, session : AsyncSession):
        super().__init__(session)
        
    async def find_by_id(self, user_id : str) -> UserInfo | None : 
        result = await self.session.execute(
            select(UserInfo)
                .options(selectinload(UserInfo.user_add))
                .where(UserInfo.userId == user_id)
        )
        
        return result.scalar_one_or_none()