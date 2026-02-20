import os
from fastapi import Depends
from dotenv import load_dotenv
from service.todo_service import TodoService
from model import Todo, TodoUpdate, notion_state
from typing import List
from service import NotionServiceImpl, get_notion_service
from datetime import datetime, timezone, timedelta

load_dotenv()

class NotionTodoServiceImpl(TodoService):
    
    def __init__(self, notion_service: NotionServiceImpl):
        self.notion_service = notion_service
    
    def get_text(self, props, key):
        try:
            items = props[key].get("title") or props[key].get("rich_text")
            if not items:
                return ""
            return items[0].get("plain_text", "")
        except:
            return ""
    
    def get_select(self, props, key):
        try:
            return props[key]["select"]["id"]
        except:
            return None
    
    def get_created_time(self, props, key):
        try:
            return self.format_kst(props[key]["created_time"])
        except:
            return None
    
    def format_kst(self, iso_str):
        try:
            dt_utc = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            dt_kst = dt_utc.astimezone(timezone(timedelta(hours=9)))
            return dt_kst.strftime("%Y-%m-%d %H:%M")
        except:
            return None
    
    def get_date(self, props, key):
        try:
            return props[key]["date"]["start"]
        except:
            return None
    
    async def get_notion_todo_service(notion_service: NotionServiceImpl = Depends(get_notion_service)):
        return NotionTodoServiceImpl(notion_service)
    
    
    # 모두 조회
    async def read_todos(self, user_id:str) -> List[Todo]:
        todos = []

        # 1. Data Source List에서 Query a data source 호출하여 page 목록(id) 조회 
        for source in notion_state.data_sources:
            
            pages = await self.notion_service.query_datasource(source["id"])
            
            for page in pages:
                props = page["properties"]
                
                status = ''
                
                if self.get_select(props, "상태") == "1":
                    status = "Pending"
                elif self.get_select(props, "상태") == "2":
                    status = "In Progress"
                elif self.get_select(props, "상태") == "3":
                    status = "Completed"
                
                todo = Todo(
                    id=page["id"],
                    title = self.get_text(props, "Name"),
                    description = self.get_text(props, "설명"),
                    status = status,
                    registDate = self.get_created_time(props, "작성일시"),
                    deadline = self.get_date(props, "마감일")
                )
                
                todos.append(todo)
        
        return todos

    # 상세 조회
    async def read_todo_detail(self, todo_id: str, user_id:str) -> Todo: 
        
        page = await self.notion_service.retrieve_page(todo_id)
        
        todo = None
        
        if page and page['id'] != '':
            
            props = page["properties"]
        
            if self.get_select(props, "상태") == "1":
                status = "Pending"
            elif self.get_select(props, "상태") == "2":
                status = "In Progress"
            elif self.get_select(props, "상태") == "3":
                status = "Completed"
            
            todo = Todo(
                id=page["id"],
                title = self.get_text(props, "Name"),
                description = self.get_text(props, "설명"),
                status = status,
                registDate = self.get_created_time(props, "작성일시"),
                deadline = self.get_date(props, "마감일")
            )
        
        return todo

    # 작업 추가
    async def create_todo(self, todo : Todo, user_id:str):
        return await self.notion_service.create_page(todo)
        
    # 작업 삭제 TODO
    def delete_todo(self, todo_id :str, user_id:str) :
        pass

    # 작업 수정
    async def update_todo(self, todo_id : str, todo_update: TodoUpdate, user_id:str) :
        
        # TODO 원본 조회
        
        return await self.notion_service.patch_page(todo_id, todo_update)