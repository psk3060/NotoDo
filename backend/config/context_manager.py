from fastapi import FastAPI
from contextlib import asynccontextmanager

from beanie import init_beanie, Document
from pymongo import AsyncMongoClient

from db.mongo import User

from dotenv import load_dotenv

from core.security import rsa_manager

from db.redis import redis_container

import redis.asyncio as redis

import os

# .env 파일 로드
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # MongoDB Client 생성
    client = AsyncMongoClient(
        f"mongodb://{os.getenv('MONGO_DATABASE_USER', '')}:{os.getenv('MONGO_DATABASE_PASSWORD', '')}"
        f"@localhost:27017/{os.getenv('MONGO_DATABASE_NAME', '')}"
        f"?authMechanism=DEFAULT&authSource={os.getenv('MONGO_DATABASE_NAME', '')}"
    )
    
    # refresh token용 redis 컨테이너
    redis_container.refresh = redis.Redis(
        host="localhost", port=6379, db=0, decode_responses=True
    )
    
    # TODO ip 관리용 redis 컨테이너 (db = 1)
    
    
    # beanie
    await init_beanie(database=client.get_default_database(), document_models=[User])
    # MongoDB Client 생성
    
    # RSA Key Pair 생성
    rsa_manager.init()
    # RSA Key Pair 생성
    
    yield
    
    client.close()
    await redis_container.refresh.close()