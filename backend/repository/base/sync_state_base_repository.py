from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from model import SyncState

from datetime import datetime

from repository.base.base_repository import BaseRepository

class SyncStateBaseRepository(BaseRepository):
    
    def __init__(self, db_session : AsyncSession):
        super().__init__(db_session)

    async def select_sync_state_one(self) -> Optional[SyncState]:
        """Sync 상태를 조회"""
        stmt = select(SyncState).where(SyncState.syncKey == "notion_sync")
        result = await self.db_session.execute(stmt)
        return result.scalars().one_or_none()



    async def insert_sync_state(self, sync_state : SyncState) -> None:
        """Sync를 저장"""
        self.db_session.add(sync_state)
        await self.db_session.commit()
        
    
    async def update_sync_state(self, lastStatus : str, sync_state : SyncState, target_date : datetime) -> None:
        """lastSyncedAt 및 lastStatus를 업데이트"""
        sync_state.lastSyncedAt = target_date
        sync_state.lastStatus = lastStatus
        await self.db_session.commit()