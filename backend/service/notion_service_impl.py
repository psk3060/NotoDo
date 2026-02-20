from model.todo.todo import Todo
import os, httpx
import re, uuid
from dotenv import load_dotenv

from model import NotionState, notion_state

from httpx import HTTPStatusError

import requests

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_VERSION = os.getenv("NOTION_VERSION")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

UUID_PATTERN = re.compile(r"^[0-9a-fA-F-]{32,36}$")

def ensure_uuid(val: str) -> str:
    if UUID_PATTERN.fullmatch(val):
        return val
    return str(uuid.uuid4())

def get_notion_headers() -> dict:
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }

def get_notion_service() :
    return NotionServiceImpl()

class NotionServiceImpl:
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

    async def close(self):
        await self.client.aclose()
    
    async def retrieve_database(self) -> NotionState:
        
        notion_state.database = await self.get(
            f"https://api.notion.com/v1/databases/{os.getenv('NOTION_DATABASE_ID')}"
        )
        
        notion_state.data_sources = notion_state.database.get("data_sources", [])
        
        return notion_state
    
    
    
    async def query_datasource(self, data_source_id : str, filter: dict | None = None) :
        url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
        
        payload = {
            "sorts": [
                {
                    "property": "작성일시",
                    "direction": "ascending"
                }
            ],
            "in_trash": False,
            "result_type": "page"
        }

        
        if filter:
            payload["filter"] = filter
            
        data = await self.post(url, payload)
        
        return [
            {
                "id": page["id"],
                "properties": page["properties"]
            }
            for page in data["results"]
        ]
        
    async def retrieve_page(self, page_id : str) : 
        page_uuid = ensure_uuid(page_id)
        
        url = f"https://api.notion.com/v1/pages/{page_uuid}"
        
        try:
            data = await self.get(url)
            
            return {
                "id": data["id"],
                "properties": data["properties"]
            }
            
        except HTTPStatusError as e:
            
            # 없음 → Create
            if e.response.status_code in (400, 404):
                return {
                    "id": '',
                    "properties": {}
                }
            raise
        
        
        
        
    async def create_page(self, todo : Todo):
        
        url = "https://api.notion.com/v1/pages"

        if todo.status == "Pending":
            status = "1" 
        elif todo.status == "In Progress":
            status = "2"
        elif todo.status == "Completed":
            status = "3"
        
        properties = {
            "상태": {"select": {"id": status}},
            "Name": {"title": [{"text": {"content": todo.title}}]},
        }

        if todo.description:
            properties["텍스트"] = {
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
        
        try :
            await self.post(url, json = payload)
        except HTTPStatusError as e:
            raise e