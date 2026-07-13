from datetime import datetime, timezone
from app.core.celery import celery_app
from app.core.enums import ActionTypeEnum
from app.models.actions import Action
from app.models.action_executions import ActionExecution, ActionStatusEnum
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
        response = httpx.post(url, json=context, timeout=10)
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

    try:
        # Step 1: Atomic pending→running transition
        updated = db.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id,
            WorkflowExecution.status == ExecutionStatusEnum.pending
        ).update({
            "status": ExecutionStatusEnum.running,
            "started_at": func.now()
        })

        if updated == 0:
            return

        db.commit()

        # Step 2: Load execution
        execution = db.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id
        ).first()

        # Step 3: Load actions ordered by action.order ascending
        actions = db.query(Action).filter(
            Action.workflow_id == execution.workflow_id
        ).order_by(Action.order.asc()).all()

        # Step 4: Execute each action with per-action tracking
        for action in actions:
            already_completed = db.query(ActionExecution).filter(
                ActionExecution.action_id == action.id,
                ActionExecution.execution_id == execution_id,
                ActionExecution.status == ActionStatusEnum.completed,
            ).first()

            if already_completed:
                continue

            action_execution = ActionExecution(
                execution_id=execution_id,
                action_id=action.id,
                order=action.order,
                started_at=datetime.now(timezone.utc),
                status=ActionStatusEnum.running,
            )
            db.add(action_execution)
            db.commit()
            db.refresh(action_execution)

            try:
                execute_action(action, context={
                    "trigger_data": execution.trigger_data
                })
                action_execution.status = ActionStatusEnum.completed
                action_execution.completed_at = datetime.now(timezone.utc)
                db.commit()

            except (httpx.TimeoutException, httpx.TransportError) as e:
                action_execution.status = ActionStatusEnum.failed
                action_execution.error_message = str(e)
                db.commit()
                raise self.retry(exc=e, countdown=60)

            except Exception as e:
                action_execution.status = ActionStatusEnum.failed
                action_execution.error_message = str(e)
                db.commit()
                raise

        # Step 5: Mark execution completed
        execution.status = ExecutionStatusEnum.completed
        execution.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        # Step 6: Mark execution failed — no retry here, retry decisions are per-action
        db.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id
        ).update({
            "status": ExecutionStatusEnum.failed,
            "error_message": str(e)
        })
        db.commit()
        raise

    finally:
        db.close()