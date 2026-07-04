from app.core.celery import celery_app
from app.core.enums import ActionTypeEnum
from app.models.actions import Action
from sqlalchemy import func
import httpx

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def execute_action(action: Action, context: dict):
    if action.type == ActionTypeEnum.log:
        message = action.config.get("message", "")
        logger.info(message)

    elif action.type == ActionTypeEnum.http_request:
        url = action.config.get("url")

        response = httpx.post(
            url,
            json=context,
            timeout=10,
        )

        response.raise_for_status()

    else:
        raise ValueError(f"Unsupported action type: {action.type}")

@celery_app.task(bind=True, max_retries=3)
def execute_workflow(self, execution_id: str):
    from app.db.database import SessionLocal
    from app.models.workflow_executions import WorkflowExecution
    from app.models.actions import Action
    from app.core.enums import ExecutionStatusEnum
    
    db = SessionLocal()

    # Step 1: Load the execution    
    try:
        updated = db.query(WorkflowExecution)\
            .filter(
                WorkflowExecution.id == execution_id,
                WorkflowExecution.status == ExecutionStatusEnum.pending
            ).update(
                {
                    "status": ExecutionStatusEnum.running,
                    "started_at": func.now()
                }
            )
                        
        if not updated:
            return
        
        db.commit()

        # Step 2: Load the execution 
        execution = (
            db.query(WorkflowExecution)
            .filter(WorkflowExecution.id == execution_id)
            .first()
        )

        # Step 3: Load actions ordered by action.order ascending
        actions = db.query(Action)\
            .filter(
                Action.workflow_id == execution.workflow_id)\
            .order_by(
                Action.order.asc()).\
            all()

        # Step 4: execute each action
        for action in actions:
            execute_action(action, context={
                "trigger_data": execution.trigger_data
            }
        )
        
        # Step 5: Transition status -> completed and set completed_at
        db.query(WorkflowExecution)\
            .filter(
                WorkflowExecution.id == execution_id)\
            .update(
                {
                    "status": ExecutionStatusEnum.completed,
                    "completed_at": func.now()
                }
                
            )

        db.commit()
    
    except Exception as e:
        # Step 6: transition status -> failed and store error message
        db.query(WorkflowExecution)\
            .filter(WorkflowExecution.id == execution_id)\
            .update(
                {
                    "status": ExecutionStatusEnum.failed,
                    "error_message": str(e)
                }
            )

        db.commit()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()

   