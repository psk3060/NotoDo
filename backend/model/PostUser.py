from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from db.postgre_engine import Base

class PostUser(Base):
    __tablename__ = "users"

    userId : Mapped[str] = mapped_column("user_id", String(36), primary_key=True)
    userName : Mapped[str] = mapped_column("user_name", String(50), nullable=False)
    password : Mapped[str] = mapped_column("user_password", String(255))
    
    isActive: Mapped[bool] = mapped_column("is_active", Boolean, nullable=True, default=True)
    isLocked: Mapped[bool] = mapped_column("is_locked", Boolean, nullable=True, default=False)
    
    failedLoginCount: Mapped[int] = mapped_column("failed_login_count", Integer, nullable=True, default=0)
    lockedUntil: Mapped[datetime | None] = mapped_column("locked_until", DateTime, nullable=True)

    lastLoginAt: Mapped[datetime | None] = mapped_column("last_login_at", DateTime, nullable=True)
    lastLoginIp: Mapped[str | None] = mapped_column("last_login_ip", String(64), nullable=True)
    
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime, nullable=True, default=datetime.now)
    