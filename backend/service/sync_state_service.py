from repository import SyncStateBaseRepository
from model import SyncState
from datetime import datetime, timezone


class SyncStateService:
    
    def __init__(self, repository : SyncStateBaseRepository):
        self.repository = repository
        
    async def get_sync_state(self) -> SyncState | None:
        """가장 마지막에 수행된 동기화 상태 조회"""
        return await self.repository.select_sync_state_one()
    
    async def save_sync_state(self, sync_state : SyncState | None, target_date : datetime) -> None:
        """저장 - 없을 경우, 새로 생성, 있을 경우 수정"""
        if sync_state:
            await self.repository.update_sync_state("success", sync_state, target_date)
        else :
            new_sync_state = SyncState(syncKey="notion_sync", lastSyncedAt=target_date, lastStatus="created")
            await self.repository.insert_sync_state(new_sync_state)
        