from datetime import datetime
from typing import Optional, Any

from config.postgre_setup import DeclarativeBase

from sqlalchemy import String, DateTime, text, JSON
from sqlalchemy.orm import Mapped, mapped_column

class SearchConditionUsage(DeclarativeBase):
    __tablename__ = "search_condition_usage"
    
    id : Mapped[int] = mapped_column('id', primary_key=True)
    userId : Mapped[Optional[str]] = mapped_column("user_id", String(36))
    save_condition : Mapped[dict[str, Any]] = mapped_column("save_condition", JSON)
    # 조건 Json_string을 Hash화 한 것. 실제 조회는 이 값을 통해 진행
    search_hash : Mapped[str] = mapped_column("search_hash", String(100), unique=True)
    registDate : Mapped[datetime] = mapped_column("regist_date", DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    modifyDate : Mapped[Optional[datetime]] = mapped_column("modify_date", DateTime(timezone=True))
    search_count : Mapped[int] = mapped_column('search_count')