import logging

from datetime import datetime, timezone, timedelta
from db.mongo.celery_config import init_mongo_for_task, close_mongo_for_task
from tasks.config.celery_config import sync_celery
from service.notion_service import NotionTaskServiceImpl
from tasks.util.task_run_util import run_async
from model import OutboxDocument
from beanie.operators import In

from db.postgres.celery_config import get_pg_session_for_tasks

from model import SyncState
from service import SyncStateService
from repository import SyncStateBaseRepository

logger = logging.getLogger(__name__)

@sync_celery.task(queue = "sync")
def from_notion_to_notodo():
    """Notion에서 Notodo에 최신 데이터 반영하기 위한 Task
        구현 
            1) 가장 마지막에 동기화 시도한 일시 저장 
            2) 1)에서의 날짜보다 Notion의 수정일자가 더 이후인 경우에만 Notion에서 조회해오기
            3) 주기는 1시간에 한 번씩
    """
    utc_now = datetime.now(timezone.utc)
    logger.info(f"[Server Sync Poller] 실행 — {utc_now.astimezone(tz=timezone(timedelta(hours=9)))}")
    run_async(task_notion_to_notodo())

KST = timezone(timedelta(hours=9))

async def task_notion_to_notodo():
    """Notion에서 Notodo로 데이터 전송"""
    
    sync_start_time = datetime.now(timezone.utc)  # 이번 실행 시작 시각 = 다음 체크포인트 후보
    
    try :
        notion_service = NotionTaskServiceImpl()
        await notion_service.retrieve_database()
        
        async with get_pg_session_for_tasks() as pg_session:
            
            sync_service = SyncStateService(SyncStateBaseRepository(pg_session))
            
            # 1) 가장 마지막에 수행된 날짜 조회(DB에서 - 데이터는 딱 하나만 존재, 없으면 None)
            sync_state = await sync_service.get_sync_state()
            
            # 있으면, 마지막 동기화 시각. 없으면 현재 시간 1시간 이전으로
            target_date = sync_state.lastSyncedAt if sync_state else sync_start_time - timedelta(hours=1)
            
            if target_date.tzinfo is None:
                target_date = target_date.replace(tzinfo=timezone.utc)
            
            filter = {
                "timestamp" : "last_edited_time",
                "last_edited_time" : {
                    "after" : target_date.astimezone(KST).strftime("%Y-%m-%d %H:%M")
                }
            }
            
            # 2) Notion에서 조회해오기 - Notion API 호출(target_date 이후, 수정된 데이터만 조회)
            temp_list = await notion_service.query_datasource(filter)
            
            logger.info(f"[Server Sync Poller] Notion에서 조회된 건수: {len(temp_list)}")
            
            if temp_list:
                # 3) TODO Notodo에 반영
                # 3-1) Notodo에만 있는 경우, 
                # 3-2) Notion에만 있는 경우,
                # 3-3) 둘 모두 있는 경우, 불필요한 수정 프로세스 방지를 위한 대책 세우기
                pass
            
            
            # 지연 시간 발생 대비 - 5분
            SYNC_SAFETY_MARGIN = timedelta(minutes=5)
            checkpoint = sync_start_time - SYNC_SAFETY_MARGIN
            
            # 4) 갱신 건 최신화 - 추가 또는 수정(TODO 추가 시 에러 datetime 관련)
            await sync_service.save_sync_state(sync_state, checkpoint)
            
            
            
    except Exception as e:
        logger.error(f"[Server Sync Poller] 에러 발생 - {e}")
    
    
    



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
        
        if events:
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
