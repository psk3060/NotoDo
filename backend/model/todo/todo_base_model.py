from datetime import datetime
from typing import Optional

from config.postgre_setup import Base

from sqlalchemy import String, DateTime, text, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

# DB INSERT용 - Hook 수동 구현
class TodoBase(Base):
    __tablename__ = "todos"
    
    id : Mapped[int] = mapped_column('id', primary_key=True)
    todoId : Mapped[str] = mapped_column("todo_id", String(50), unique=True)
    title : Mapped[str] = mapped_column("todo_title", String(50))
    status : Mapped[str] = mapped_column("todo_status", String(12))
    deadline : Mapped[Optional[str]] = mapped_column("deadline", String(14))
    description : Mapped[Optional[str]] = mapped_column("description", Text)
    userId : Mapped[Optional[str]] = mapped_column("user_id", String(36))
    priority : Mapped[Optional[str]] = mapped_column("todo_priority", String(5))
    isTrash : Mapped[bool] = mapped_column("is_trash", default = False)
    trashDate : Mapped[Optional[datetime]] = mapped_column("trash_date", DateTime(timezone=True))
    registDate : Mapped[datetime] = mapped_column("regist_date", DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    lastModified : Mapped[Optional[datetime]] = mapped_column("last_modified", DateTime(timezone=True))
    
    comments : Mapped[list["TodoCommentBase"]] = relationship(
        "TodoCommentBase",
        back_populates="todo",
        lazy="noload",
        cascade="all, delete-orphan"
    )
    
    
class TodoCommentBase(Base):
    __tablename__ = "todo_comments"
    
    id : Mapped[int] = mapped_column('id', primary_key=True)
    commentId : Mapped[str] = mapped_column("comment_id", String(50), unique=True)
    todoId : Mapped[str] = mapped_column(
        "todo_id",
        String(50),
        ForeignKey("todos.todo_id")
    )
    
    author : Mapped[str] = mapped_column("author", String(30))
    commentText : Mapped[str] = mapped_column("comment_text")
    isTrash : Mapped[bool] = mapped_column("is_trash", default = False)
    registDate : Mapped[datetime] = mapped_column("regist_date",  DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    lastModified : Mapped[Optional[datetime]] = mapped_column("last_modified", DateTime(timezone=True))
    trashDate : Mapped[Optional[datetime]] = mapped_column("trash_date", DateTime(timezone=True))
    
    todo : Mapped["TodoBase"] = relationship(
            "TodoBase",
            back_populates="comments"
    )