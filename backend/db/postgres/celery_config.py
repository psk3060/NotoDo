from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.postgres.config import DATABASE_URL

@asynccontextmanager
async def get_pg_session_for_tasks():
    """
        중복 방지 및 Task마다 엔진을 새로 생성하기 위해 asynccontextmanager
        종료 시 Dispose
    """
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(
        bind = engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try :
        async with AsyncSessionLocal() as session:
            yield session
    finally:
        await engine.dispose()
