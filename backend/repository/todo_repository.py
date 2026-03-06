import math

from datetime import datetime
from sqlalchemy import func, select, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from model import Todo, TodoComment
from model import TodoBase, TodoCommentBase
from model import TodoListRequest, TodoListResponse

class TodoRepository:
    def __init__(self, session : AsyncSession):
        self.session = session
    
    def set_query_conditions(self, listRequest : TodoListRequest) :
        conditions = [
            TodoBase.userId == listRequest.userId,
            TodoBase.isTrash == False
        ]
        
        if listRequest.status:
            conditions.append(TodoBase.status == listRequest.status)
        
        if listRequest.priority:
            conditions.append(TodoBase.priority == listRequest.priority)
        
        if listRequest.title:
            conditions.append(TodoBase.title.ilike(f"%{listRequest.title}%"))
            
        return conditions
        
    
    async def select_list(self, listRequest : TodoListRequest) -> TodoListResponse:
        
        result = None
        
        if listRequest.isPaging :
            result = await self.session.execute(
            select(TodoBase)
                .where(*self.set_query_conditions(listRequest))
                .limit(listRequest.pageSize)
                .offset((listRequest.currentPage - 1) * listRequest.pageSize)    
            )
        else :
            result = await self.session.execute(
            select(TodoBase)
                .where(*self.set_query_conditions(listRequest))
            )
        
        
        todos = result.scalars().all()
        
        total_result = await self.session.execute(
            select(func.count()).select_from(TodoBase)
            .where(*self.set_query_conditions(listRequest))
        )
        
        total = total_result.scalar()
        
        response = TodoListResponse(
                data=[Todo.model_validate(todo) for todo in todos],
                total=total,
                totalPages=math.ceil(total / listRequest.pageSize)
        )
        
        return response
    
    
    async def create_todo(self, todo : Todo) : 
        # 1. Todo → TodoBase 생성
        todo_entity = TodoBase(
            id = todo.id,
            title = todo.title,
            status = todo.status,
            priority = todo.priority,
            deadline = todo.deadline,
            userId = todo.userId,
            description = todo.description
        )
        
        # 2. Insert
        self.session.add(todo_entity)
        
        # 3. Commit
        await self.session.commit()
        
    
    async def select_by_id(self, todo_id, user_id) :
        
        stmt = select(TodoBase).where(and_(
                TodoBase.id == todo_id,
                TodoBase.userId == user_id
        )).options(selectinload(TodoBase.comments))
        
        result = await self.session.execute(stmt)
        
        todo = result.scalar_one_or_none()
        
        response = None
        
        if todo:
            response = Todo.model_validate(todo)
        
        return response
    
    async def update(self, todo_id, todo_update: Todo):
        await self.session.execute(
            update(TodoBase)
                .where(and_(
                    TodoBase.id == todo_id,
                    TodoBase.userId == todo_update.userId
                ))
                .values(
                    title = todo_update.title,
                    priority = todo_update.priority,
                    status = todo_update.status,
                    description = todo_update.description,
                    deadline = todo_update.deadline
                )
        )
        
        await self.session.commit()
        
    async def delete(self, todo : Todo ) :
        
        await self.session.execute(
            update(TodoBase)
                .where(and_(
                    TodoBase.id == todo.id,
                    TodoBase.userId == todo.userId
                ))
                .values(isTrash = True, trashDate = datetime.now())
        )
        
        await self.session.commit()
        
    async def create_todo_comment(self, comment : TodoComment) :
        
        comment_entity = TodoCommentBase(
            commentId = comment.commentId, 
            id = comment.id,
            author = comment.author,
            commentText = comment.commentText,
            isTrash = comment.isTrash,
            lastModified = datetime.now()
        )
        
        self.session.add(comment_entity)
        
        # 3. Commit
        await self.session.commit()