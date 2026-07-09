import logging

from datetime import datetime

from model import OutboxDTO, OutboxDocument

logger = logging.getLogger(__name__)

class OutboxDocumentRepository : 
    
    async def insert(dto : OutboxDTO, processed: bool) :
        outbox = OutboxDocument(**dto.model_dump(), processed=processed, created_at = datetime.now())
        await outbox.insert()
        return outbox
    
    async def selectDistinctPidList(self) -> list[str]:
        collection = OutboxDocument.get_pymongo_collection()
        
        result = None
        
        try :
            result = await collection.distinct(
                        "parent_id",
                        {
                            "processed" : False,
                            "event_caller" : 'todo',
                            "event_type" : {"$in": ["updated", "deleted"]},
                            "parent_id" : {"$ne": None},
                        }
                    )
        except Exception as ex:
            logger.error(f"[Server Sync Repository] 에러 발생 - {ex}")
        
        return result
        