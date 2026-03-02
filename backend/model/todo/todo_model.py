from pydantic import BaseModel, Field
from typing import Optional
from config.postgre_setup import Base

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from typing import List


class TodoComment(BaseModel):
    commentId : Optional[str] = None
    todoId : Optional[str] = None
    lastModified : Optional[str] = None
    author : Optional[str] = None
    commentText : Optional[str] = None

class Todo(BaseModel):
    id:Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    registDate:Optional[str] = None
    deadline:Optional[str] = None
    description: Optional[str] = None
    userId : Optional[str] = None
    priority : Optional[str] = None
    comments : List[TodoComment] = Field(default_factory=list)

class TodoListRequest(BaseModel):
    currentPage : Optional[int] = 0
    pageSize : Optional[int] = 0
    title :Optional[str] = None
    status: Optional[str] = None
    priority : Optional[str] = None
    userId : Optional[str] = None

class TodoListResponse(BaseModel):
    data : List[Todo] = []
    total: Optional[int] = 0
    totalPages: Optional[int] = 0


# DB INSERT용 - Hook 수동 구현
class TodoBase(Base):
    __tablename__ = "todos"
    
    todoId : Mapped[str] = mapped_column("todo_id", String(30), primary_key=True)
    todoTitle : Mapped[str] = mapped_column("todo_title", String(50), nullable=False)
    todoStatus : Mapped[str] = mapped_column("todo_status", String(1), nullable=False)
    registDate : Mapped[str] = mapped_column("regist_date", String(14), nullable=False)
    deadline : Mapped[str] = mapped_column("deadline", String(14), nullable=True)
    description : Mapped[str] = mapped_column("description", Text, nullable=True)
    userId : Mapped[str] = mapped_column("user_id", String(36), nullable=True)
    todoPriority : Mapped[str] = mapped_column("todo_priority", String(5), nullable=True)