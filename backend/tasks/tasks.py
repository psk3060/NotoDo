import logging
import asyncio

from datetime import datetime, timezone

from tasks.init_db import _init_beanie
from tasks.celery_app import celery

from service.notion_service import NotionTaskServiceImpl
from model.todo.todo_outbox_model import TodoOutbox

logger = logging.getLogger(__name__)

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Outbox Poller (Celery Beat — 주기적 실행 - 정합성 맞추기 위함)
@celery.task
def process_outbox():
    logger.info(f"[Outbox Poller] 실행 — {datetime.now(timezone.utc)}")
    run_async(_process_outbox())

# Worker
@celery.task(bind = True, max_retries=5)
def sync_to_notion(self, event_id : str):
    
    try :
        run_async(_sync_to_notion(event_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    
async def _process_outbox():
    
    client = await _init_beanie()
    
    try :
        events = await TodoOutbox.find(TodoOutbox.processed == False).to_list()
        logger.info(f"[Outbox Poller] 미처리 건수: {len(events)}")
        for event in events:
            sync_to_notion.delay(str(event.id))
    finally:
        await client.close()
    
    
async def _sync_to_notion(event_id : str):
    
    client = await _init_beanie()
    
    try :
        event = await TodoOutbox.get(event_id)
        notion_service = NotionTaskServiceImpl()
        
        if event.event_type == "updated":
            await notion_service.patch_page(event.todo_id, event.payload["after"], False)
            
        elif event.event_type == "deleted":
            await notion_service.patch_page(event.todo_id, event.payload["before"], True)
        
        event.processed = True
        await event.save()
        
    finally :
        await client.close()    
    
    
    