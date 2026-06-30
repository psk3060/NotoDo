from repository import OutboxDocumentRepository

from model import OutboxDTO

from tasks.config.celery_config import sync_celery, condition_celery



class OutboxRegistServiceImpl():
    
    def __init__(self, repository : OutboxDocumentRepository):
        self.repository = repository
        
    async def insert(self, dto : OutboxDTO, processed : bool, queueName : str | None ):
        # 1. 등록
        outbox = self.repository.insert(dto, processed)
        
        # 2. celery 호출
        if queueName:
            if queueName == "sync":
                sync_celery.send_task("tasks.sync.notion_tasks.sync_to_notion", args=[str(outbox.id)], queue="sync")
            elif queueName == "condition":
                condition_celery.send_task("tasks.condition.condition_tasks.task_save_condition_db", args=[str(outbox.id)], queue="condition")
        