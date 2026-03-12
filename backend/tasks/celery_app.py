from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()
celery = Celery(broker=os.getenv("REDIS_URL", "redis://localhost:6379/2"))

# 윈도우 환경에서는 prefork가 구조적으로 불안정하다고 하여 solo로 개발
celery.conf.worker_pool = "solo"

celery.conf.beat_schedule = {
    "process-outbox-every-30-seconds": {
        "task":     "tasks.tasks.process_outbox",
        "schedule": 30.0,  # 30초마다
    },
}