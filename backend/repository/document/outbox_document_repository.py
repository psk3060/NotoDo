from datetime import datetime

from model import OutboxDTO, OutboxDocument

class OutboxDocumentRepository : 
    
    async def insert(dto : OutboxDTO, processed: bool) :
        outbox = OutboxDocument(**dto.model_dump(), processed=processed, created_at = datetime.now())
        await outbox.insert()
        return outbox