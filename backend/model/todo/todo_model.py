from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from typing import List


class TodoComment(BaseModel):
    commentId : Optional[str] = None
    todoId : Optional[str] = None
    lastModified : Optional[str] = None
    author : Optional[str] = None
    commentText : Optional[str] = None
    registDate:Optional[datetime] = None
    isTrash : Optional[bool] = False
    trashDate : Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
    
class Todo(BaseModel):
    todoId:Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    registDate:Optional[datetime] = None
    deadline:Optional[str] = None
    description: Optional[str] = None
    userId : Optional[str] = None
    priority : Optional[str] = None
    isTrash : Optional[bool] = False
    trashDate : Optional[datetime] = None
    comments : List[TodoComment] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True, frozen=False)
    
class TodoListRequest(BaseModel):
    currentPage : Optional[int] = 0
    pageSize : Optional[int] = 10
    title :Optional[str] = None
    status: Optional[str] = None
    priority : Optional[str] = None
    userId : Optional[str] = None
    isPaging : Optional[bool] = False

class TodoListResponse(BaseModel):
    data : List[Todo] = Field(default_factory=list)
    total: Optional[int] = 0
    totalPages: Optional[int] = 0