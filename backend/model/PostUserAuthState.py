from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime
from db.postgre_engine import Base

class UserAuthState(Base):
    __tablename__ = "user_auth_state"
    
    userId : Mapped[str] = mapped_column("user_id", String(36), primary_key=True)
    
    # Refresh Token 무효화 기준
    refresh_revoked_after: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)
    
    # 비밀번호 변경 일시
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)