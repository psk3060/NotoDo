from fastapi import FastAPI
from contextlib import asynccontextmanager

# mongodb
# from beanie import init_beanie
# from pymongo import AsyncMongoClient

from dotenv import load_dotenv

from core.security import rsa_manager

from db.redis import redis_container

import redis.asyncio as redis

from db.postgre_engine import engine, Base

import os
import model.PostUser  # 모델 로드 중요

# .env 파일 로드
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # MongoDB Client 생성
    
    # client = AsyncMongoClient(
    #     f"mongodb://{os.getenv('MONGO_DATABASE_USER', '')}:{os.getenv('MONGO_DATABASE_PASSWORD', '')}"
    #     f"@localhost:27017/{os.getenv('MONGO_DATABASE_NAME', '')}"
    #     f"?authMechanism=DEFAULT&authSource={os.getenv('MONGO_DATABASE_NAME', '')}"
    # )
    
    # await init_beanie(database=client.get_default_database(), document_models=[User])
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
        await conn.run_sync(Base.metadata.create_all)
    
    # Postgre 테이블 생성
    
    
    # RSA Key Pair 생성
    rsa_manager.init()
    # RSA Key Pair 생성
    
    yield
    
    # client.close()
    await redis_container.refresh.close()
    await redis_container.ip.close()