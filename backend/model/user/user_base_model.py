from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from config.postgre_setup import Base

class UserInfo(Base):
    '''사용자 정보'''
    __tablename__ = "users"

    userId : Mapped[str] = mapped_column("user_id", String(36), primary_key=True)
    userName : Mapped[str] = mapped_column("user_name", String(50), nullable=False)
    password : Mapped[str] = mapped_column("user_password", String(255))
    
    email : Mapped[str] = mapped_column("email", String(100))
    
    isActive: Mapped[bool] = mapped_column("is_active", Boolean, nullable=True, default=True)
    isLocked: Mapped[bool] = mapped_column("is_locked", Boolean, nullable=True, default=False)
    
    failedLoginCount: Mapped[int] = mapped_column("failed_login_count", Integer, nullable=True, default=0)
    lockedUntil: Mapped[datetime | None] = mapped_column("locked_until", DateTime, nullable=True)

    lastLoginAt: Mapped[datetime | None] = mapped_column("last_login_at", DateTime, nullable=True)
    lastLoginIp: Mapped[str | None] = mapped_column("last_login_ip", String(64), nullable=True)
    
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime, nullable=True, default=datetime.now)
    
    user_add: Mapped["UserAdd"] = relationship(
        "UserAdd",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
class UserAdd(Base):
    '''사용자 부가 정보'''
    __tablename__ = "user_add"
    
    user_id: Mapped[str] = mapped_column(
        "user_id",
        String(36),
        ForeignKey("users.user_id"),
        primary_key=True
    )
    
    notionId : Mapped[str] = mapped_column("notion_id", String(100), nullable=True)    
    
    user: Mapped["UserInfo"] = relationship(
            "UserInfo",
            back_populates="user_add"
    )


class UserAuthState(Base):
    __tablename__ = "user_auth_state"
    
    userId : Mapped[str] = mapped_column("user_id", String(36), primary_key=True)
    
    # Refresh Token 무효화 기준
    refresh_revoked_after: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)
    
    # 비밀번호 변경 일시
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)