from fastapi import FastAPI
from contextlib import asynccontextmanager

from beanie import init_beanie, Document
from pymongo import AsyncMongoClient

from db.mongo import User

from dotenv import load_dotenv

from core.security import rsa_manager

import os

# .env 파일 로드
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    client = AsyncMongoClient(
        f"mongodb://{os.getenv('MONGO_DATABASE_USER', '')}:{os.getenv('MONGO_DATABASE_PASSWORD', '')}"
        f"@localhost:27017/{os.getenv('MONGO_DATABASE_NAME', '')}"
        f"?authMechanism=DEFAULT&authSource={os.getenv('MONGO_DATABASE_NAME', '')}"
    )
    await init_beanie(database=client.get_default_database(), document_models=[User])
    rsa_manager.init()
    yield
    
    client.close()