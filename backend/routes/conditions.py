from fastapi import APIRouter, Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession

from service import OutboxRegistServiceImpl
from service import SearchConditionService, SearchConditionClientServiceImpl

from repository import OutboxDocumentRepository, ConditionBaseRepository

from model import ConditionDeleteRequestDTO

from db.postgres.client_config import get_pg_session

router = APIRouter(
    prefix="/conditions",
    tags=["conditions"]
)

def get_condition_service (
    session : AsyncSession = Depends(get_pg_session)    
) -> SearchConditionService: 
    return SearchConditionClientServiceImpl(ConditionBaseRepository(session), OutboxRegistServiceImpl(OutboxDocumentRepository))

@router.get("")
async def select_usage_condition_list(request: Request, usage_condition_service : SearchConditionService = Depends(get_condition_service)):
    '''Modal에서 호출
    5개만 호출할 것이고, 파라미터도 회원ID만 있으므로 별도의 RequestDTO는 불필요
    '''
    return await usage_condition_service.selectList(request.state.user)


@router.delete("")
async def delete_usage_condition(request : Request, requestDto : ConditionDeleteRequestDTO, usage_condition_service : SearchConditionService = Depends(get_condition_service)) : 
    await usage_condition_service.delete_condition(request.state.user, requestDto.ids)
    