import asyncio
import logging

from tasks.config.celery_init_db import _init_beanie
from tasks.config.celery_config import condition_celery

from config.postgre_setup import AsyncSessionLocal

from model.todo.todo_outbox_model import TodoOutbox

from service.search_condition_service import UsageSearchConditionServiceImpl

from utils.string_utils import replace_hash_string, json_to_string

logger = logging.getLogger(__name__)

def run_async(coro):
    return asyncio.run(coro)

# Task - Redis 저장소에 조건 추가되었을 경우, 수행될 Task
@condition_celery.task(queue="condition")
def task_save_condition_db(event_id : str):
    
    try :
        run_async(save_condition_db(event_id))
    except Exception as exc:
        logger.error("fail usage search condition save \n", exc)

# Redis 저장소에 조건 추가 되었을 경우, DB에 저장
async def save_condition_db(event_id : str):
    
    client = await _init_beanie()
    
    try:
        # Event 조회(MongoDB)
        event = await TodoOutbox.get(event_id)
        
        userId = event.user_id
        eventPayload = event.payload
        
        async with AsyncSessionLocal() as session:
            
            # Task의 경우, 세션을 별도로 생성하기를 권장
            conditionService = UsageSearchConditionServiceImpl(session)
            
            # eventPayload가 비어있지 않다면, event의 event_type 체크
            if eventPayload:
                # 1) event의 event_type 체크
                if event.event_type == "query":
                    # 저장
                    await conditionService.save_condition(userId, eventPayload['condition'])
                    
                    # 3) Outbox 처리 내역 확인(Redis 메시지 삭제 및 Outbox 처리 완료 확인)
                    event.processed = True
                    await event.save()
            
    finally:
        await client.close()
    