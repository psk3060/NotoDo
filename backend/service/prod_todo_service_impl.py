import os
from model.todo.todo_model import TodoComment
from model.todo.notion_todo_priority import from_notion_priority_id
from model.todo.notion_todo_status import from_notion_status_id
from utils.notion_util import get_date_time, get_date, get_select, get_select_name, get_status, get_status_name, get_text
from fastapi import Depends
from dotenv import load_dotenv
from service.todo_service import TodoService
from model import Todo, notion_state
from typing import List
from service import NotionServiceImpl, get_notion_service


load_dotenv()

class ProdTodoServiceImpl(TodoService):
    
    def __init__(self, notion_service: NotionServiceImpl):
        self.notion_service = notion_service
    
    async def get_notion_todo_service(notion_service: NotionServiceImpl = Depends(get_notion_service)):
        return ProdTodoServiceImpl(notion_service)
    
    # 모두 조회
    async def read_todos(self, user_id:str) -> List[Todo]:
        todos = []

        # print(notion_state.data_sources)
        
        for source in notion_state.data_sources:
            pages = await self.notion_service.query_datasource(source["id"])
            
            for page in pages:
                props = page["properties"]
                
                todo = Todo(
                    id=page["id"],
                    title = get_text(props, "작업명"),
                    status = get_status_name(props, "상태"),
                    registDate = get_date_time(page, 'created_time'),
                    deadline = get_date(props, '마감일'),
                    priority = get_select_name(props, "우선순위")
                )
                
                todos.append(todo)
        
        
        
        return todos

    # 상세 조회
    async def read_todo_detail(self, todo_id: str, user_id:str) -> Todo: 
        
        page = await self.notion_service.retrieve_page(todo_id)
        
        todo = None
        
        if page and page['id'] != '':
            
            props = page["properties"]

            todo = Todo(
                id=page["id"],
                title = get_text(props, "작업명"),
                description = get_text(props, "설명"),
                status = from_notion_status_id(get_status(props, "상태")),
                registDate = get_date_time(page, 'created_time'),
                deadline = get_date(props, '마감일'),
                priority = from_notion_priority_id(get_select(props, "우선순위"))
            )
        
        if todo:
            comments = await self.notion_service.retrieve_reply_list(todo.id)
            
            if len(comments) > 0:
                for comment in comments:
                    todo.comments.append(TodoComment(commentId=comment["id"], todoId=todo.id, commentText=comment['body'], author=comment['author'], lastModified=comment['lastModified']))
            
        return todo

    # 작업 추가
    async def create_todo(self, todo : Todo, user_id:str):
        await self.notion_service.create_page(todo)
        
    # 작업 삭제
    async def delete_todo(self, todo_id :str, user_id:str) :
        await self.notion_service.patch_page(todo_id, None, True)

    # 작업 수정
    async def update_todo(self, todo_id : str, todo_update: Todo, user_id:str) :
        await self.notion_service.patch_page(todo_id, todo_update)
        
    async def create_comment(self, comment : TodoComment) :
        await self.notion_service.create_reply(comment)