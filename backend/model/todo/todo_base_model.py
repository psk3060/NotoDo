from datetime import datetime

from config.postgre_setup import Base

from sqlalchemy import String, DateTime, Boolean, text, ForeignKey, Text, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

# DB INSERT용 - Hook 수동 구현
class TodoBase(Base):
    __tablename__ = "todos"
    
    id : Mapped[str] = mapped_column("todo_id", String(50), primary_key=True)
    title : Mapped[str] = mapped_column("todo_title", String(50), nullable=False)
    status : Mapped[str] = mapped_column("todo_status", String(10), nullable=False)
    registDate : Mapped[datetime] = mapped_column("regist_date", DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    lastModified : Mapped[datetime] = mapped_column("last_modified", DateTime(timezone=True), nullable=True)
    deadline : Mapped[str] = mapped_column("deadline", String(14), nullable=True)
    description : Mapped[str] = mapped_column("description", Text, nullable=True)
    userId : Mapped[str] = mapped_column("user_id", String(36), nullable=True)
    priority : Mapped[str] = mapped_column("todo_priority", String(5), nullable=True)
    isTrash : Mapped[bool] = mapped_column("is_trash", Boolean, nullable=False, default = False)
    trashDate : Mapped[datetime] = mapped_column("trash_date", DateTime, nullable=True)
    
    comments : Mapped[list["TodoCommentBase"]] = relationship(
        "TodoCommentBase",
        back_populates="todo",
        lazy="noload",
        cascade="all, delete-orphan"
    )
    
class TodoCommentBase(Base):
    __tablename__ = "todo_comments"
    
    commentId : Mapped[str] = mapped_column("comment_id", String(30), primary_key=True)
    id : Mapped[str] = mapped_column(
        "todo_id",
        String(50),
        ForeignKey("todos.todo_id")
    )
    registDate : Mapped[datetime] = mapped_column("regist_date",  DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    lastModified : Mapped[datetime] = mapped_column("last_modified", DateTime(timezone=True), nullable=True)
    author : Mapped[str] = mapped_column("author", String(30), nullable=False)
    commentText : Mapped[str] = mapped_column("comment_text", Text, nullable=False)
    isTrash : Mapped[str] = mapped_column("is_trash", Boolean, nullable=True, default = False)
    trashDate : Mapped[datetime] = mapped_column("trash_date", DateTime(timezone=True), nullable=True)
    
    todo : Mapped["TodoBase"] = relationship(
            "TodoBase",
            back_populates="comments"
    )