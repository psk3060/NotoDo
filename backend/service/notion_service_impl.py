import os, httpx

from dotenv import load_dotenv

from model import NotionState, notion_state

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

        body = {}
        if filter:
            body["filter"] = filter
            
        data = await self.post(url, payload)
        
        return [
            {
                "id": page["id"],
                "properties": page["properties"]
            }
            for page in data["results"]
        ]