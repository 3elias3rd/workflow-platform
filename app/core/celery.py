from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery("workflow-platform", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,
    imports="app.workers.tasks"
)

celery_app.conf.beat_schedule = {
    "detect-orphaned-executions": {
        "task": "app.workers.maintenance.detect_orphaned_executions",
        "schedule": 300.0,
    },
}