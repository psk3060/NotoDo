from datetime import datetime, timezone

from model.todo.todo_outbox_model import TodoCommentOutboxDTO, TodoOutbox, TodoOutboxDTO, TodoCommentOutbox

class TodoOutboxRepository : 
    async def insert(dto : TodoOutboxDTO, processed: bool) :
        outbox = TodoOutbox(**dto.model_dump(), processed=processed, created_at = datetime.now())
        await outbox.insert()
        return outbox
        
    async def insertComment(dto : TodoCommentOutboxDTO, processed : bool):
        outbox = TodoCommentOutbox(**dto.model_dump(), processed=processed, created_at = datetime.now())
        await outbox.insert()
        return outbox