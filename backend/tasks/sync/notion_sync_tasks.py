import logging

from datetime import datetime, timezone, timedelta

from db.mongo.celery_config import init_mongo_for_task, close_mongo_for_task

from tasks.config.celery_config import sync_celery

from service.notion_service import NotionTaskServiceImpl
from tasks.util.task_run_util import run_async

from model import OutboxDocument

from beanie.operators import In

logger = logging.getLogger(__name__)



@sync_celery.task(queue = "sync")
def from_notion_to_notodo():
    """Notion에서 Notodo에 최신 데이터 반영하기 위한 Task
        구현 
            1) 가장 마지막에 수행된 날짜 및 반영 건 보관
            2) 1)에서의 날짜보다 Notion의 수정일자가 더 큰 경우에만 Notion에서 조회해오기
            3) 주기는 30분에 한 번씩
            4) Notion 데이터를 Notodo에 강제로 덮어쓰기
    """
    
    pass


@sync_celery.task(queue="sync")
def process_outbox():
    """Notodo → Notion 미처리 건 탐색을 하기 위한 Task(Beatㄹ르 통해 매 15초마다 실행)"""
    utc_now = datetime.now(timezone.utc)
    logger.info(f"[Outbox Poller] 실행 — {utc_now.astimezone(tz=timezone(timedelta(hours=9)))}")
    run_async(find_target())


async def find_target():
    """Notodo → Notion 미처리 건 탐색"""
    mongo_client = await init_mongo_for_task()

    try:
        events = await OutboxDocument.find(
            In(OutboxDocument.event_type, ["updated", "deleted"])
            , OutboxDocument.processed == False
        ).to_list()
        logger.info(f"[Outbox Poller] 미처리 건수: {len(events)}")
        
        for event in events:
            sync_to_notion.delay(str(event.id))
        
    finally:
        await close_mongo_for_task(mongo_client)
    


# 정합성 맞추기 위한 Task(최대 재시도 횟수, 시도 별 딜레이 등) : 재시도 하지 않을 경우, bind 불필요(self 사용)
@sync_celery.task(bind = True, max_retries=5, default_retry_delay=10, acks_late=True, queue="sync")
def sync_to_notion(self, event_id : str):
    
    utc_now = datetime.now(timezone.utc)
    logger.info(f"[Sync Job] 실행 — {utc_now.astimezone(tz=timezone(timedelta(hours=9)))}")
    
    try :
        run_async(_sync_to_notion(event_id))
    except Exception as exc:
        # 지수 백오프
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        logger.info(f"[Sync Job] 종료 — {utc_now.astimezone(tz=timezone(timedelta(hours=9)))}")

async def _sync_to_notion(event_id : str):
    
    mongo_client = await init_mongo_for_task()
    
    try :
        event = await OutboxDocument.get(event_id)
        
        notion_service = NotionTaskServiceImpl()
        
        if event.event_type == "updated":
            await notion_service.patch_page(event.parent_id, event.payload["after"])
        elif event.event_type == "deleted":
            await notion_service.patch_page(event.parent_id, {"in_trash" : True})
        
        event.processed = True
        await event.save()
        
    finally :
        await close_mongo_for_task(mongo_client)
