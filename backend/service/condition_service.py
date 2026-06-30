import logging

from abc import ABC, abstractmethod

from typing import Any

from model import OutboxDTO
from model.dto.condition import convert_list

from sqlalchemy.ext.asyncio import AsyncSession
from repository import ConditionBaseRepository

from service.outbox_service import OutboxRegistServiceImpl

from utils import string_utils as string

logger = logging.getLogger(__name__)

# 자주 사용한 검색 조건, 저장 검색 조건을 위한 Service
class SearchConditionService(ABC):
    
    @abstractmethod
    def save_condition(self, userId : str, payload : dict[str, Any]) : pass
    
    @abstractmethod
    def delete_condition(self, userId : str, conditionId : str) : pass
    
    @abstractmethod
    async def selectList(self, userId : str) : pass
    
    @abstractmethod
    def selectOne(self, conditionId : str) : pass


class SearchConditionTaskServiceImpl(SearchConditionService):
    '''Task에서 호출하는 검색조건 관리 서비스(등록만 사용)'''
    def __init__(self, session : AsyncSession):
        self.session = session
        
    async def save_condition(self, userId : str, payload : dict[str, Any]):
        repository = ConditionBaseRepository(self.session)
        
        # 문자열을 Hash로 변환
        hash_data = string.replace_hash_string(string.json_to_string(payload))

        count = await repository.count(hash_data)
        
        if count == 0:
            await repository.insert(userId, payload, hash_data)
        else:
            await repository.increate_count(hash_data)
        
        await self.session.commit()

    def delete_condition(self, userId : str, conditionId : str): raise NotImplementedError
    def selectList(self, userId : str): raise NotImplementedError
    def selectOne(self, conditionId : str): raise NotImplementedError


class SearchConditionClientServiceImpl(SearchConditionService):
    '''클라이언트에서 사용하는 Service'''
    def __init__(self, condition_repository : ConditionBaseRepository, outbox_service : OutboxRegistServiceImpl):
        self.condition_repository = condition_repository
        self.outbox_service = outbox_service

    async def save_condition(self, userId : str, payload : dict[str, Any]):
        '''조건 저장'''
        
        # Outbox에 등록 후, 내부에서 Task 호출
        await self.outbox_service.insert(
            dto = OutboxDTO(
                        db_id = None,
                        event_caller = "condition_task",
                        parent_id = None,
                        child_id = None,
                        event_type = 'query', 
                        user_id = userId, 
                        token_jti = None, 
                        payload = {
                            "condition": payload
                        }
            ), 
            processed = False,
            queueName = "condition"
        )
        
        
        
    def delete_condition(self, userId : str, conditionId : str):
        '''저장된 조건 삭제'''
        
        # 1. 조회 조건 조회
        
        # 2. 조회 조건과 회원 ID 검증
        
        # 3. 조회 조건 삭제
        
        pass
    
    
    
    async def selectList(self, userId : str):
        '''조회'''
        # 5건만 반환
        temp_result = await self.condition_repository.selectListLimit(userId, 5)
        
        response = convert_list(temp_result)
        
        return response
        
    
    # TODO 한 건만 조회
    def selectOne(self): raise NotImplementedError


