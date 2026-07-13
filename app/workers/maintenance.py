from celery.schedules import crontab
from app.core.celery import celery_app
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@celery_app.task()
def detect_orphaned_executions():

    from app.models.workflow_executions import WorkflowExecution
    from app.core.enums import ExecutionStatusEnum
    from datetime import datetime, timedelta, UTC
    from app.db.database import SessionLocal

    db = SessionLocal()

    TIME_DELTA = timedelta(minutes=10)
    cutoff = datetime.now(UTC) - TIME_DELTA


    try: 
        result = db.query(WorkflowExecution)\
            .filter(
                WorkflowExecution.status == ExecutionStatusEnum.running, WorkflowExecution.started_at < cutoff)\
            .update(
                {
                    "status": ExecutionStatusEnum.failed,
                    "error_message": "worker_timeout"
                }
            )
        db.commit()
        logger.info(f"Orphan detection: marked {result} executions as failed")
        
    finally:
        db.close()


