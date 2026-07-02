import os
import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager

# Mongo
from db.mongo.client_config import connect_mongo, disconnect_mongo
from db.postgres.client_config import init_postgres, close_postgres

from dotenv import load_dotenv

import redis.asyncio as redis

from service.notion_service import NotionApiServiceImpl

logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

@asynccontextmanager
async def lifespan(app : FastAPI):
    await _startup(app)
    try :
        yield
    finally:
        await _shutdown(app)
        

# ─── Startup ────────────────────────────────────────────────────────────────

async def _startup(app : FastAPI):
    # Mongo 
    await _init_mongo()
    await _init_postgres()
    await _init_redis()
    _init_rsa()
    await _init_notion_mutable(app)


async def _init_mongo():
    logger.info("MongoDB 초기화 중...")
    await connect_mongo()
    logger.info("MongoDB 연결 완료")


async def _init_postgres():
    logger.info("PostgreSQL 테이블 생성 중...")
    await init_postgres()
    logger.info("PostgreSQL 테이블 생성 완료")


async def _init_redis():
    logger.info("Redis 연결 중...")
    # refresh token용 redis 컨테이너(db = 0)
    
    from core.redis_container import redis_container
    redis_container.refresh = redis.Redis(
        host="localhost", port=6379, db=0, decode_responses=True
    )
    
    # ip 관리용 redis 컨테이너 (db = 1)
    redis_container.ip = redis.Redis(
        host="localhost", port=6379, db=1, decode_responses=True
    )
    logger.info("Redis 연결 완료")


def _init_rsa():
    logger.info("RSA Key Pair 생성 중...")
    from core.rsa_mamanger import rsa_manager
    rsa_manager.init()
    logger.info("RSA Key Pair 생성 완료")


async def _init_notion_mutable(app : FastAPI):
    
    if os.getenv("TODO_ENV", "local") != "prod":
        app.state.notion_container = None
        app.state.notion_service = None
        return
    
    logger.info("Notion 연동 중...")
    
    notion_service = NotionApiServiceImpl()
    container = await notion_service.retrieve_database()
    
    if container is None:
        logger.error("Notion 연동 실패: 데이터베이스 조회 불가")
        app.state.notion_container = None
        app.state.notion_service = None
        return
    
    app.state.notion_container = container
    app.state.notion_service = notion_service
    logger.info("Notion 연동 완료")
                

# ─── Shutdown ────────────────────────────────────────────────────────────────

async def _shutdown(app : FastAPI):
    await _close_mongo()
    await _close_postgres()
    await _close_redis()
    await _close_notion(app)

async def _close_mongo():
    try:
        await disconnect_mongo()
        logger.info("MongoDB 연결 해제")
    except Exception:
        logger.exception("MongoDB 해제 중 오류")

async def _close_postgres():
    try:
        await close_postgres()
        logger.info("PostgreSQL 연결 해제")
    except Exception:
        logger.exception("PostgreSQL 해제 중 오류")

async def _close_redis():
    try:
        from core.redis_container import redis_container
        if redis_container.refresh:
            await redis_container.refresh.close()
        if redis_container.ip:
            await redis_container.ip.close()
        logger.info("Redis 연결 해제")
    except Exception:
        logger.exception("Redis 해제 중 오류")

async def _close_notion(app : FastAPI):
    if os.getenv("TODO_ENV", "local") != "prod":
        return
    try :
        # 서비스 컨테이너에서 연결 해제
        notion_service = getattr(app.state, "notion_service", None)
        if notion_service:
            await notion_service.close()
        
        logger.info("Notion 연결 해제")
    except Exception:
        logger.exception("Notion 해제 중 오류")
        
    