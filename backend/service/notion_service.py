from abc import ABC, abstractmethod

from utils.notion_utils import get_date_time
from utils.notion_convert_utils  import to_notion_status_id, to_notion_status_value, to_notion_priority_id, to_notion_priority_value
from utils.string_utils import ensure_uuid

from model.todo.todo_model import Todo, TodoComment
import os, httpx
from dotenv import load_dotenv

from model import NotionState, notion_state

from httpx import HTTPStatusError

import logging

logger = logging.getLogger(__name__)

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_VERSION = os.getenv("NOTION_VERSION")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def get_notion_headers() -> dict:
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }

def get_notion_service() :
    return NotionApiServiceImpl()
    
    

class NotionService(ABC):
    
    def __init__(self):
        self.headers = get_notion_headers()
        self.client = httpx.AsyncClient(headers=self.headers)
    
    async def get(self, url: str):
        res = await self.client.get(url, headers=self.headers)
        res.raise_for_status()
        return res.json()
    
    async def post(self, url: str, json: dict):
        res = await self.client.post(url, headers=self.headers, json=json)
        res.raise_for_status()
        return res.json()

    async def patch(self, todo_id : str, json:dict):
        res = await self.client.patch(f"https://api.notion.com/v1/pages/{todo_id}", headers=self.headers, json=json)
        res.raise_for_status()
        return res.json()
    
    async def close(self):
        await self.client.aclose()
    
    @abstractmethod
    def retrieve_database() -> NotionState:
        pass
    
    @abstractmethod
    def query_datasource(data_source_id : str, filter: dict | None = None) -> dict :
        pass
    
    @abstractmethod
    def retrieve_page(page_id : str) -> dict : 
        pass
    
    @abstractmethod
    def create_page(todo : Todo) -> dict :
        pass
    
    @abstractmethod
    def patch_page(todo_id : str, todo : Todo | dict | None = None, is_trash : bool | None = False) -> dict :
        pass
    
    @abstractmethod
    def retrieve_reply_list( page_id : str) -> list:
        pass
    
    @abstractmethod
    def create_reply(comment : TodoComment) -> dict :
        pass


class NotionApiServiceImpl(NotionService):
    def __init__(self):
        self.headers = get_notion_headers()
        self.client = httpx.AsyncClient(headers=self.headers)
    
    async def get(self, url: str):
        
        res = await self.client.get(url, headers=self.headers)
        res.raise_for_status()
        return res.json()
    
    async def post(self, url: str, json: dict):
        res = await self.client.post(url, headers=self.headers, json=json)
        res.raise_for_status()
        return res.json()

    async def patch(self, url : str, json:dict):
        res = await self.client.patch(url, headers=self.headers, json=json)
        res.raise_for_status()
        return res.json()
    
    async def close(self):
        await self.client.aclose()
    
    async def retrieve_database(self) -> NotionState:
        
        url = f"https://api.notion.com/v1/databases/{os.getenv('NOTION_DATABASE_ID')}"
        
        try:
            notion_state.database = await self.get(url)
            
            notion_state.data_sources = notion_state.database.get("data_sources", [])
            
            return notion_state
            
        except HTTPStatusError as e:
            return None
        

    async def query_datasource(self, data_source_id : str, filter: dict | None = None) :
        url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
        
        payload = {
            "sorts": [
                {
                    "property": "우선순위",
                    "direction": "ascending"
                },
                {
                    "property": "상태",
                    "direction": "ascending"
                },
                {
                    "property": "마감일",
                    "direction": "ascending"
                }
            ],
            "in_trash": False,
            "archived": False,
            "result_type": "page"
        }
        
        if filter:
            
            filter_list = []
            
            if "작업명" in filter:
                filter_list.append({ "title" : {"contains": filter['작업명']}, "property" : "작업명" })
            
            if "상태" in filter:
                filter_list.append({ "status": { "equals": to_notion_status_value(filter['상태']) }, "property" : "상태" })
            
            if "우선순위" in filter:
                filter_list.append({ "select": { "equals": to_notion_priority_value(filter['우선순위']) }, "property" : "우선순위" })
            
            payload["filter"] = {
                "and" : filter_list
            }
            
        try:
            data = await self.post(url, payload)
            
            pages = [
                {
                    "id": page["id"],
                    "created_time" : page["created_time"],
                    "properties": page["properties"]
                }
                for page in data["results"]
            ]
            
            result = {
                "pages" : pages
                , "has_more" : data["has_more"]
            }
            
            return result
        except HTTPStatusError as e:
            
            return {
                "pages" : {
                    "id" : "",
                    "created_time" : None,
                    "properties" : {}
                },
                "has_more" : None
            }
    
    async def retrieve_page(self, page_id : str) : 
        page_uuid = ensure_uuid(page_id)
        
        url = f"https://api.notion.com/v1/pages/{page_uuid}"
        
        try:
            data = await self.get(url)
            
            return {
                "id": data["id"],
                "created_time" : data["created_time"],
                "properties": data["properties"]
            }
            
        except HTTPStatusError as e:
            
            # 없음 → Create
            if e.response.status_code in (400, 404):
                return {
                    "id": '',
                    "created_time" : '',
                    "properties": {}
                }
            raise
        
    
    async def create_page(self, todo : Todo):
        
        url = "https://api.notion.com/v1/pages"

        properties = {
            "상태": {"status": {"id": to_notion_status_id(todo.status)}},
            "작업명": {"title": [{"text": {"content": todo.title}}]},
            "우선순위": { "select": { "id": to_notion_priority_id(todo.priority) } },
        }

        if todo.description:
            properties["설명"] = {
                "rich_text": [{"text": {"content": todo.description}}]
            }

        if todo.deadline:
            properties["마감일"] = {
                "date": {"start": todo.deadline}
            }

        # TODO DataSource 선택 가능하도록 확장
        payload = {
            "parent": {"data_source_id": notion_state.data_sources[0]["id"]},
            "properties": properties
        }
        
        create_response = None
        
        try :
            create_response = await self.post(url, json = payload)
        except HTTPStatusError as e:
            raise e
        
        if create_response and "id" in create_response:
            create_id = create_response["id"]
        
        return {
            "isSuccess" : True,
            "id" : create_id
        }
        
    async def patch_page(self, todo_id : str, todo : Todo | dict | None = None, is_trash : bool | None = False) -> dict :
        
        properties = {}
        
        if todo:
            
            properties = {
                "상태": {"status": {"id": to_notion_status_id(todo.status)}},
                "작업명": {"title": [{"text": {"content": todo.title}}]},
                "우선순위": { "select": { "id": to_notion_priority_id(todo.priority) } },
            }
            
            if todo.description:
                properties["설명"] = {
                    "rich_text": [{"text": {"content": todo.description}}]
                }
            # 내용 없을 경우 공백
            else :
                properties["설명"] = {"rich_text": []}
            
            
            if todo.deadline:
                properties["마감일"] = {
                    "date": {"start": todo.deadline}
                }
            else :
                properties["마감일"] = { "date": {} }
        
        
        payload = {
            "properties": properties,
            "in_trash" : is_trash
        }
        
        
        try :
            await self.patch(todo_id, json = payload)
        except HTTPStatusError as e:
            raise e
        
        # TODO
        return {
            "isSuccess" : True,
            "message" : ""
        }
    
    async def retrieve_reply_list(self, page_id : str):
        url = f"https://api.notion.com/v1/comments?block_id={page_id}"
        
        try:
            comments = await self.get(url)
            
            return [
                {
                    "id" : comment["id"]
                    , "body" : comment["rich_text"][0]['plain_text']
                    , "author" : comment["display_name"]['resolved_name']
                    , "lastModified" : get_date_time(comment, "last_edited_time")
                }
                for comment in comments["results"]
            ] 
            
        except HTTPStatusError as e:
            print(e)
            return []
    
    async def create_reply(self, comment : TodoComment) -> dict :
        
        url = "https://api.notion.com/v1/comments"
        
        payload = {
            "rich_text": [{"text": {"content": comment.commentText}}],
            "parent": {
                "page_id": comment.todoId,
                "type": "page_id"
            },
            # TODO 첨부파일
            "attachments": [],
            "display_name": {
                "type": "custom",
                "custom": { "name": comment.author }
            }
        }

        create_response = None
        
        try :
            create_response = await self.post(url, json = payload)
        except HTTPStatusError as e:
            raise e
        
        if create_response and "id" in create_response:
            create_id = create_response["id"]
        
        # TODO
        return {
            "isSuccess" : True,
            "id" : create_id
        }
        

class NotionTaskServiceImpl(NotionService):
    
    def __init__(self):
        self.headers = get_notion_headers()
        self.client = httpx.AsyncClient(headers=self.headers)
    
    def retrieve_database() -> NotionState:
        pass
    
    def query_datasource(data_source_id : str, filter: dict | None = None) -> dict :
        pass
    
    def retrieve_page(page_id : str) -> dict : 
        pass
    
    def create_page(todo : Todo) -> dict :
        pass
    
    def retrieve_reply_list( page_id : str) -> list:
        pass
    
    def create_reply(comment : TodoComment) -> dict :
        pass
    
    async def patch_page(self, todo_id : str, body : dict | None = None) -> dict :
        
        try :
            await self.patch(todo_id, json = body)
        except HTTPStatusError as e:
            raise e
        
        # TODO
        return {
            "isSuccess" : True,
            "message" : ""
        }
    