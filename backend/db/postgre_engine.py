import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL



load_dotenv()

DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=os.getenv('POSTGRE_DATABASE_USER', ''),
    password=os.getenv('POSTGRE_DATABASE_PASSWORD', ''),
    host="localhost",
    port=5432,
    database=os.getenv('POSTGRE_DATABASE_DB', ''),
)

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()