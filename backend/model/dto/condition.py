from pydantic import BaseModel, Field
from typing import Optional, List

class ConditionDTO(BaseModel):
    conditionId:Optional[str] = Field(None, description="조건 ID. 삭제 및 상세 조회에 사용")
    title: Optional[str] = Field(None, description="제목")
    status: Optional[str] = Field(None, description="상태")
    priority : Optional[str] = Field(None, description="우선순위")
    registDate:Optional[str] = Field(None, description="등록일시")
    
class ConditionListResponse(BaseModel):
    data : List[ConditionDTO] = Field(default_factory=list)    
