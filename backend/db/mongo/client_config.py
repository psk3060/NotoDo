# Client 사용하는 Mongo
# lifespan 기반, 앱 시작 ~ 종료까지 유지(AsyncMongoClient는 앱 시작 시 1회 생성 및 초기화. 연결 재사용)
from pymongo import AsyncMongoClient
from beanie import init_beanie
from db.mongo.config import MONGO_URL, DOCUMENT_MODELS

_client : AsyncMongoClient | None = None

async def connect_mongo():
    global _client
    _client = AsyncMongoClient(MONGO_URL)
    await init_beanie(
        database = _client.get_default_database(),
        document_models=DOCUMENT_MODELS
    )
    
async def disconnect_mongo():
    global _client
    if _client:
        await _client.aclose()
        _client = None    