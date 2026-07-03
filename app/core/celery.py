from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery("workflow-platform", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(task_track_started=True)