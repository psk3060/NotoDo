from db.postgres.config import DATABASE_URL
from db.postgres.base import Base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20)
AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_postgres():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_postgres():
    await engine.dispose()

# FastAPI 의존성 주입을 위한 메서드
async def get_pg_session():
    async with AsyncSessionLocal() as session:
        yield session
