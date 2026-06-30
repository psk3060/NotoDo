import math

from datetime import datetime
from sqlalchemy import func, select, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from utils import notion_utils as notion

from model import Todo, TodoComment
from model import TodoBase, TodoCommentBase
from model import TodoListRequest, TodoListResponse

class TodoBaseRepository:
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
            todoId = todo.todoId,
            title = todo.title,
            status = todo.status,
            priority = todo.priority,
            deadline = todo.deadline,
            userId = todo.userId,
            description = todo.description
        )
        
        # 2. Insert
        self.session.add(todo_entity)
        
        # 3. flush
        await self.session.flush()
        
        # 반환 받기(Service에서 Commit)
        await self.session.refresh(todo_entity)
        
        return todo_entity
        
    
    async def select_object_by_id(self, todo_id, user_id) :
        stmt = select(TodoBase).where(and_(
                TodoBase.todoId == todo_id,
                TodoBase.userId == user_id
        ))
        
        result = await self.session.execute(stmt)
        
        return result.scalar_one_or_none()
        
    
    async def select_by_id(self, todo_id, user_id) :
        
        stmt = select(TodoBase).where(and_(
                TodoBase.todoId == todo_id,
                TodoBase.userId == user_id
        )).options(selectinload(TodoBase.comments))
        
        result = await self.session.execute(stmt)
        
        todo = result.scalar_one_or_none()
        
        response = None
        
        if todo:
            response = Todo.model_validate(todo)
        
        return response
    
    async def update(self, todo_id : str, todo_update: Todo):
        
        todo_entity = await self.select_object_by_id(todo_id, todo_update.userId)
        
        if todo_entity is None:
            raise Exception()
        
        todo_entity.title = todo_update.title
        todo_entity.priority = todo_update.priority
        todo_entity.status = todo_update.status
        todo_entity.description = todo_update.description
        todo_entity.deadline = todo_update.deadline
        
        # 3. flush
        await self.session.flush()
        await self.session.refresh(todo_entity)
        
        return todo_entity
        
    async def delete(self, todo_id, user_id ) :
        
        todo_entity = await self.select_object_by_id(todo_id, user_id)
        
        if todo_entity is None:
            raise Exception()
            
        todo_entity.isTrash = True
        todo_entity.trashDate = datetime.now()
        
        await self.session.flush()
        await self.session.refresh(todo_entity)
        
        return todo_entity
    
    
        
    async def create_todo_comment(self, comment : TodoComment) -> TodoCommentBase :
        
        comment_entity = TodoCommentBase(
            commentId = comment.commentId, 
            todoId = comment.todoId,
            author = comment.author,
            commentText = comment.commentText,
            isTrash = comment.isTrash,
            lastModified = datetime.now()
        )
        
        self.session.add(comment_entity)
        
        # 3. flush
        await self.session.flush()
        
        # 반환 받기(Service에서 Commit)
        await self.session.refresh(comment_entity)
        
        return comment_entity
        

    def to_dict(self, entity: TodoBase) -> dict:
        
        properties = {
            "상태": {"status": {"id": notion.to_notion_status_id(entity.status)}},
            "작업명": {"title": [{"text": {"content": entity.title}}]},
            "우선순위": { "select": { "id": notion.to_notion_priority_id(entity.priority) } },
        }
        
        if entity.description:
            properties["설명"] = {
                "rich_text": [{"text": {"content": entity.description}}]
            }
        # 내용 없을 경우 공백
        else :
            properties["설명"] = {"rich_text": []}
            
            
        if entity.deadline:
            properties["마감일"] = {
                "date": {"start": entity.deadline}
            }
        
        
        payload = {
            "properties": properties
        }
        
        return payload
    
    
    def to_comment_dict(self, entity : TodoCommentBase) -> dict:
        '''등록만 있음'''
        payload = {
            "rich_text": [{"text": {"content": entity.commentText}}],
            "parent": {
                "page_id": entity.todoId,
                "type": "page_id"
            },
            # TODO 첨부파일
            "attachments": [],
            "display_name": {
                "type": "custom",
                "custom": { "name": entity.author }
            }
        }
        
        return payload
    
    
    
    
    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
    
    
    