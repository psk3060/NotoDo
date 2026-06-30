from pydantic import BaseModel, Field
from typing import Optional, List

from model.base import FrequentlySearchedConditions

from utils import notion_utils as notion

class ConditionDTO(BaseModel):
    id : Optional[str] = Field(None, description="조건 ID. 삭제 및 상세 조회에 사용")
    title: Optional[str] = Field(None, description="제목")
    status: Optional[str] = Field(None, description="상태")
    priority : Optional[str] = Field(None, description="우선순위")
    registDate:Optional[str] = Field(None, description="등록일시")
    
class ConditionListResponse(BaseModel):
    data : List[ConditionDTO] = Field(default_factory=list)    


def convert_vo_to_dto(vo : FrequentlySearchedConditions) -> ConditionDTO:
    return ConditionDTO(
        id = str(vo.conditionId),
        status = notion.to_notion_status_label(vo.saveCondition.get("status")),
        priority = notion.to_notion_priority_label(vo.saveCondition.get("priority")),
        title=vo.saveCondition.get("title"),
        registDate=vo.registDate.isoformat() if vo.registDate else None
    )
    
def convert_list(temp_result : list[FrequentlySearchedConditions]) -> ConditionListResponse:
    return ConditionListResponse(
        data=[convert_vo_to_dto(vo) for vo in temp_result]
    )