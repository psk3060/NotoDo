import logging

from repository import OutboxDocumentRepository

from model import OutboxDTO

from tasks.config.celery_config import sync_celery, condition_celery

logger = logging.getLogger(__name__)

class OutboxRegistServiceImpl():
    '''Outbox에 등록하면서, 바로 처리하는 서비스(등록말고는 없을 것으로 예상)'''
    
    def __init__(self, repository : OutboxDocumentRepository):
        self.repository = repository
        
    async def insert(self, dto : OutboxDTO, processed : bool, queueName : str | None ):
        # 1. 등록
        outbox = await self.repository.insert(dto, processed)
        
        # 2. celery 호출
        if queueName:
            if queueName == "sync":
                sync_celery.send_task("tasks.sync.notion_tasks.sync_to_notion", args=[str(outbox.id)], queue="sync")
            elif queueName == "condition":
                condition_celery.send_task("tasks.condition.condition_tasks.task_save_condition_db", args=[str(outbox.id)], queue="condition")
        
        return outbox

class OutboxListServiceImpl():
    """Outbox에서 조회 - Task에서 사용"""
    def __init__(self, repository : OutboxDocumentRepository):
        self.repository = repository
        
    
    async def selectDistinctPidList(self) -> list[str]:
        
        result = None
        
        try :
            result =  await self.repository.selectDistinctPidList()
        except Exception as e:
            logger.error(f"[Server Sync Service] 에러 발생 - {e}")
            
        return result    
        
    