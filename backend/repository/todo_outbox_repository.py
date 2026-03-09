from datetime import datetime, timezone

from model.todo.todo_outbox_model import TodoOutbox, TodoOutboxDTO

class TodoOutboxRepository : 
    async def insert(dto : TodoOutboxDTO, processed: bool) :
        await TodoOutbox(**dto.model_dump(), processed=processed, created_at = datetime.now(timezone.utc)).insert()
        
    