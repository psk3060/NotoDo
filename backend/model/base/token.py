from db.postgres.base import Base

from datetime import  datetime

from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from typing import Optional

class TokenBlock(Base):
    """Token Black List
    필수 : access_token.jti, refresh_token.jti(Index)
    expire_at : (expire_at - 현재시각) ttl
    event_type : logout 또는 refresh(토큰 갱신)
    status : 상태
    user_id : 회원ID
    """
    __tablename__ = "token_black_list"
    
    blockId : Mapped[int] = mapped_column('block_id', primary_key=True)
    accessJti : Mapped[Optional[str]] = mapped_column("access_jti", String(200), comment="Access Token JTI")
    refreshJti : Mapped[Optional[str]] = mapped_column("refresh_jti", String(200), comment="Refresh Token JTI")
    expireAt : Mapped[Optional[datetime]] = mapped_column("expire_at", DateTime(timezone=True), comment="만료일시")
    # 불필요
    # blockStatus : Mapped[Optional[str]] = mapped_column("block_status", String(5), comment="차단 상태(불필요)")
    eventType : Mapped[Optional[str]] = mapped_column("event_type", String(10), comment="logout 또는 refresh(토큰 갱신)")
    userId : Mapped[Optional[str]] = mapped_column("user_id", String(30), comment="회원ID")
    registAt : Mapped[Optional[datetime]] = mapped_column("regist_at", DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), comment="등록일시")
    # 불필요
    # blockAt : Mapped[Optional[datetime]] = mapped_column("block_at", DateTime(timezone=True), nullable= True, comment="차단일시(불필요)")
    
    