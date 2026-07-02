from datetime import datetime, timezone

from typing import Optional, Any

from sqlalchemy import String, DateTime, text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres.base import Base

class SyncState(Base):
    """하나의 Sync 상태를 관리하는 모델 - 마지막 동기화 시도 일시를 저장"""
    __tablename__ = "sync_state"

    stateId : Mapped[int] = mapped_column('state_id', BigInteger, primary_key=True, autoincrement=True)
    syncKey: Mapped[str] = mapped_column('sync_key', String(100), nullable=False, unique=True)
    lastSyncedAt: Mapped[Optional[datetime]] = mapped_column('last_synced_at', nullable=True)
    lastStatus: Mapped[Optional[str]] = mapped_column('last_status', String(20), nullable=True)
    registAt: Mapped[datetime] = mapped_column('regist_at', DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    