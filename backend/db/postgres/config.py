# 공통상수

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
    f"@localhost:5432/{os.getenv('PG_DATABASE')}"
)