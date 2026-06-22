import os

from model.todo.todo_outbox_model import TodoCommentOutbox, TodoOutbox
from model import RefreshTokenLog
from fastapi import FastAPI
from contextlib import asynccontextmanager

# mongodb
from beanie import init_beanie
from pymongo import AsyncMongoClient

from dotenv import load_dotenv

from core.security import rsa_manager

import redis.asyncio as redis

from config.redis_setup import redis_container
from config.postgre_setup import engine, DeclarativeBase

from service.notion_service import NotionApiServiceImpl
from model.todo.search_condition import SearchConditionUsage


# .env 파일 로드
load_dotenv()

@asynccontextmanager
async def lifespan(_: FastAPI):
    # MongoDB Client 생성
    
    client = AsyncMongoClient(
        f"mongodb://{os.getenv('MONGO_DATABASE_USER', '')}:{os.getenv('MONGO_DATABASE_PASSWORD', '')}"
        f"@localhost:27017/{os.getenv('MONGO_DATABASE_NAME', '')}"
        f"?authMechanism=DEFAULT&authSource={os.getenv('MONGO_DATABASE_NAME', '')}"
    )
    
    await init_beanie(database=client.get_default_database(), document_models=[RefreshTokenLog, TodoOutbox, TodoCommentOutbox])
    # MongoDB Client 생성
    
    # refresh token용 redis 컨테이너
    redis_container.refresh = redis.Redis(
        host="localhost", port=6379, db=0, decode_responses=True
    )
    
    # ip 관리용 redis 컨테이너 (db = 1)
    redis_container.ip = redis.Redis(
        host="localhost", port=6379, db=1, decode_responses=True
    )
    # ip 관리용 redis 컨테이너 (db = 1)
    
    # Postgre 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.create_all)
    
    # Postgre 테이블 생성
    
    # RSA Key Pair 생성
    rsa_manager.init()
    # RSA Key Pair 생성
    
    # Notion 연동
    if os.getenv('TODO_ENV', 'local') == 'prod':
        notion_service = NotionApiServiceImpl()
        # Retrieve a database에서 DATABASE_ID 입력하여, data_sources 목록 조회
        await notion_service.retrieve_database()

    yield
    
    # client.close()
    await redis_container.refresh.close()
    await redis_container.ip.close()
    if os.getenv('TODO_ENV', 'local') == 'prod':
        await notion_service.close()