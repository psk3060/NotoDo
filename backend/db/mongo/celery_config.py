from pymongo import AsyncMongoClient
from beanie import init_beanie

from db.mongo.config import MONGO_URL, DOCUMENT_MODELS

async def init_mongo_for_task() -> AsyncMongoClient:
    """Task의 루프 안에서 호출"""
    client = AsyncMongoClient(MONGO_URL)
    await init_beanie(
        database = client.get_default_database(),
        document_models=DOCUMENT_MODELS
    )
    return client


async def close_mongo_for_task(client : AsyncMongoClient):
    """Task의 루프 안에서 호출하여 자원 해제"""
    await client.aclose()