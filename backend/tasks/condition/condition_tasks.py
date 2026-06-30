import asyncio
import logging
from datetime import datetime, timezone, timedelta

from tasks.config.celery_config import condition_celery

from db.mongo.celery_config import init_mongo_for_task, close_mongo_for_task
from db.postgres.celery_config import get_pg_session_for_tasks

from model import OutboxDocument

from tasks.util.task_run_util import run_async
from service.condition_service import SearchConditionTaskServiceImpl

logger = logging.getLogger(__name__)

# Task - Redis 저장소에 조건 추가되었을 경우, 수행될 Task
@condition_celery.task(queue="condition")
def task_save_condition_db(event_id : str):
    utc_now = datetime.now(timezone.utc)
    logger.info(f"[조건 저장] 실행 — {utc_now.astimezone(tz=timezone(timedelta(hours=9)))}")
    
    try :    
        run_async(save_condition_db(event_id))
    except Exception as exc:
        logger.error(f"[조건 저장] 실패: {exc}", exc_info=True)
    finally:
        logger.info(f"[조건 저장] 완료 — {utc_now.astimezone(tz=timezone(timedelta(hours=9)))}")
    
# Redis 저장소에 조건 추가 되었을 경우, DB에 저장
async def save_condition_db(event_id : str):
    
    mongo_client = await init_mongo_for_task()
    
    try :
        # Event 조회(MongoDB)
        event = await OutboxDocument.get(event_id)
    
        userId = event.user_id
        eventPayload = event.payload
        
        if event.event_type == "query" and bool(eventPayload):
            
            async with get_pg_session_for_tasks() as pg_session:
                conditionService = SearchConditionTaskServiceImpl(pg_session)

                await conditionService.save_condition(userId, eventPayload['condition'])
                
                event.processed = True
                await event.save()
                
    finally : 
        await close_mongo_for_task(mongo_client)
    
    
    