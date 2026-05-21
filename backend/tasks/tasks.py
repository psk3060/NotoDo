import logging
import asyncio

from datetime import datetime, timezone, timedelta

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
    
    utc_now = datetime.now(timezone.utc)
    
    logger.info(f"[Outbox Poller] 실행 — {utc_now.astimezone(tz=timezone(timedelta(hours=9)))}")
    run_async(_process_outbox())

async def _process_outbox():
    
    client = await _init_beanie()
    
    try :
        events = await TodoOutbox.find(TodoOutbox.processed == False).to_list()
        logger.info(f"[Outbox Poller] 미처리 건수: {len(events)}")
        for event in events:
            sync_to_notion.delay(str(event.id))
    finally:
        await client.close()

# Outbox Poller (Celery Beat — 주기적 실행 - 정합성 맞추기 위함)


# Worker
@celery.task(bind = True, max_retries=5, default_retry_delay=10, acks_late=True)
def sync_to_notion(self, event_id : str):
    
    try :
        run_async(_sync_to_notion(event_id))
    except Exception as exc:
        # 지수 백오프
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

async def _sync_to_notion(event_id : str):
    
    client = await _init_beanie()
    
    try :
        
        event = await TodoOutbox.get(event_id)
        
        notion_service = NotionTaskServiceImpl()
        
        if event.event_type == "updated":
            await notion_service.patch_page(event.todo_id, event.payload["after"])
        elif event.event_type == "deleted":
            await notion_service.patch_page(event.todo_id, {"in_trash" : True})
        
        event.processed = True
        await event.save()
        
    finally :
        await client.close()
        

        