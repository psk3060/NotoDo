from datetime import datetime
from sqlalchemy import func, select, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from model.todo.search_condition import SearchConditionUsage

class UsageConditionRepository:
    
    def __init__(self, session : AsyncSession):
        self.session = session
        
    async def count(self, hash_data : str) -> int:
        total_result = await self.session.execute(
            select(func.count()).select_from()
                .where(SearchConditionUsage.search_hash == hash_data)
        )
        
        result = total_result.scalar()
        
        return result
    
    async def insert(self, userId, payload, hash_data):
        
        entity = SearchConditionUsage(
            userId = userId,
            save_condition = payload,
            search_hash = hash_data,
            search_count = 1
        )
        
        self.session.add(entity)
        
        await self.session.flush()
        
        await self.session.refresh(entity)
        
        return entity
    
    async def increate_count(self, hash_data):
        entity = await self.select_object_by_id(hash_data)
        
        search_count = entity.search_count
        
        entity.search_count = search_count + 1
        
        await self.session.flush()
        
        await self.session.refresh(entity)
        
        return entity
    
        
    async def select_object_by_id(self, hash_data) :
        stmt = select(SearchConditionUsage).where(and_(
                SearchConditionUsage.search_hash == hash_data
        ))
        
        result = await self.session.execute(stmt)
        
        return result.scalar_one_or_none()