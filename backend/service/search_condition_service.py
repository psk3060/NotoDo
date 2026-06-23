from abc import ABC, abstractmethod

from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from repository.usage_condition_repository import UsageConditionRepository

from utils.string_utils import replace_hash_string, json_to_string

# 자주 사용한 검색 조건, 저장 검색 조건을 위한 Service
class SearchConditionService(ABC):
    
    @abstractmethod
    def save_condition():
        # 조건 저장 - Count 이후, Insert 또는 업데이트 포함
        pass
    
    @abstractmethod
    def delete_condition():
        pass
    
    @abstractmethod
    def selectList():
        pass
    
    @abstractmethod
    def selectOne():
        pass
    
    
# 자주 사용한 검색 조건 - 조회 버튼을 통해 등록되는 조회 조건    
class UsageSearchConditionServiceImpl(SearchConditionService):
    
    def __init__(self, session : AsyncSession):
        self.session = session
    
    async def save_condition(self, userId : str, payload : dict[str, Any]):
        repository = UsageConditionRepository(self.session)
        
        # 문자열을 Hash로 변환
        hash_data = replace_hash_string(json_to_string(payload))

        count = await repository.count(hash_data)
        
        if count == 0:
            await repository.insert(userId, payload, hash_data)
        else:
            await repository.increate_count(hash_data)
        
        await self.session.commit()
        
    
    def delete_condition():
        pass
    
    def selectList():
        pass
    
    def selectOne():
        pass