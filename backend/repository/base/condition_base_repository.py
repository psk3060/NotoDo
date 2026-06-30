from datetime import datetime
from sqlalchemy import func, select, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from model import FrequentlySearchedConditions

class ConditionBaseRepository:
    
    def __init__(self, session : AsyncSession):
        self.session = session
    
    async def count(self, hash_data : str) -> int:
        '''한 건만 등록하기 위한 Count'''
        total_result = await self.session.execute(
            select(func.count()).select_from()
                .where(FrequentlySearchedConditions.saveConditionHash == hash_data)
        )
        
        result = total_result.scalar()
        
        return result
    
    async def insert(self, userId, payload, hash_data):
        '''등록'''
        entity = FrequentlySearchedConditions(
            userId = userId,
            saveCondition = payload,
            saveConditionHash = hash_data,
            searchCount = 1
        )
        
        self.session.add(entity)
        
        await self.session.flush()
        
        await self.session.refresh(entity)
        
        return entity
    
    async def increate_count(self, hash_data):
        '''검색 횟수 1 증가'''
        entity = await self.select_object_by_id(hash_data)
        
        searchCount = entity.searchCount
        
        entity.searchCount = searchCount + 1
        
        await self.session.flush()
        
        await self.session.refresh(entity)
        
        return entity
    
        
    async def select_object_by_id(self, hash_data) :
        '''한 건만 조회 - Hash Data'''
        stmt = select(FrequentlySearchedConditions).where(and_(
                FrequentlySearchedConditions.saveConditionHash == hash_data
        ))
        
        result = await self.session.execute(stmt)
        
        return result.scalar_one_or_none()
    
    async def selectListLimit(self, userId : str, limitValue : int):
        '''목록 조회 - 5건만'''
        
        stmt = select(FrequentlySearchedConditions).where(
                FrequentlySearchedConditions.userId == userId
        ).order_by(FrequentlySearchedConditions.searchCount.desc()).limit(limitValue)
        
        result = await self.session.execute(stmt)
        
        return result.scalars().all()
    
    async def deleteCondition(self, hashData):
        
        pass