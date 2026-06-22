import os
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from beanie import init_beanie

from model.todo.todo_outbox_model import TodoOutbox

load_dotenv()

MONGO_URL = (
    f"mongodb://{os.getenv('MONGO_DATABASE_USER', '')}:{os.getenv('MONGO_DATABASE_PASSWORD', '')}"
    f"@localhost:27017/{os.getenv('MONGO_DATABASE_NAME', '')}"
    f"?authMechanism=DEFAULT&authSource={os.getenv('MONGO_DATABASE_NAME', '')}"
)


async def _init_beanie():
    client = AsyncMongoClient(MONGO_URL)
    await init_beanie(
        database        = client.get_default_database(),
        document_models = [TodoOutbox]
    )
    return client