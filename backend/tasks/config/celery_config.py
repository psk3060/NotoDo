from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

sync_celery = Celery(broker=os.getenv("NOTION_REDIS_URL", "redis://localhost:6379/2"))
condition_celery = celery = Celery(broker=os.getenv("CONDITION_REDIS_URL", "redis://localhost:6379/3"))

# 윈도우 환경에서는 prefork가 구조적으로 불안정하다고 하여 solo로 개발
sync_celery.conf.worker_pool = "solo"
condition_celery.conf.worker_pool = "solo"

# 스케줄러 정의
sync_celery.conf.beat_schedule = {
    "process-notion-sync": {
        "task":     "tasks.sync.notion_sync_tasks.process_outbox",
        "schedule": 15.0,
        "options": {
            "queue": "sync",
        }
    },
}