from pydantic import BaseModel, Field

from datetime import datetime
from typing import Optional, Any, List

from sqlalchemy import String, DateTime, text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres.base import Base

# 자주 찾는 검색 조건
class FrequentlySearchedConditions(Base):
    __tablename__ = "frequently_searched_conditions"
    conditionId : Mapped[int] = mapped_column('condition_id', primary_key=True)
    userId : Mapped[Optional[str]] = mapped_column("user_id", String(36))
    saveCondition : Mapped[dict[str, Any]] = mapped_column("save_condition", JSON)
    saveConditionHash : Mapped[str] = mapped_column("search_hash", String(100), unique=True)
    registDate : Mapped[datetime] = mapped_column("regist_date", DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    modifyDate : Mapped[Optional[datetime]] = mapped_column("modify_date", DateTime(timezone=True))
    searchCount : Mapped[int] = mapped_column('search_count')




    

