# celery, fastapi 공유 - Mongo에서 사용하는 공통상수

import os
from dotenv import load_dotenv
from model import OutboxDocument, RefreshTokenLogDocument

load_dotenv()

MONGO_URL = (
    f"mongodb://{os.getenv('MONGO_DATABASE_USER')}:{os.getenv('MONGO_DATABASE_PASSWORD')}"
    f"@localhost:27017/{os.getenv('MONGO_DATABASE_NAME')}"
    f"?authMechanism=DEFAULT&authSource={os.getenv('MONGO_DATABASE_NAME')}"
)

DOCUMENT_MODELS = [RefreshTokenLogDocument, OutboxDocument]