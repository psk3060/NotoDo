import asyncio
import logging

from tasks.config.celery_init_db import _init_beanie
from tasks.config.celery_config import condition_celery

from model.todo.todo_outbox_model import TodoOutbox

from service.search_condition_service import UsageSearchConditionServiceImpl

logger = logging.getLogger(__name__)

def run_async(coro):
    return asyncio.run(coro)

# Task - Redis 저장소에 조건 추가되었을 경우, 수행될 Task
@condition_celery.task(queue="condition")
def task_save_condition_db(event_id : str):
    
    try :
        run_async(save_condition_db(event_id))
    except Exception as exc:
        # TODO
        logger.error("fail usage search condition save")

# Redis 저장소에 조건 추가 되었을 경우, DB에 저장
async def save_condition_db(event_id : str):
    
    client = await _init_beanie()
    
    try:
        # Event 조회(MongoDB)
        event = await TodoOutbox.get(event_id)
        
        userId = event.user_id
        eventPayload = event.payload
        
        conditionService = UsageSearchConditionServiceImpl()
        
        # eventPayload가 비어있지 않다면, event의 event_type 체크
        if eventPayload:
            # 1) event의 event_type 체크
            if event.event_type == "query":
                # 저장
                await conditionService.save_condition(userId, eventPayload)

            
            # 3) Outbox 처리(무조건 처리)
            event.processed = True
            await event.save()
            
    finally:
        await client.close()
    