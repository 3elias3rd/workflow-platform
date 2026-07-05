from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.workflow_executions import WorkflowExecution
from app.core.deps import get_current_user
from app.schemas.auth import CurrentUser


router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("/{execution_id}")
def get_execution(
    execution_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)):

    execution = db.query(WorkflowExecution)\
        .filter(
            WorkflowExecution.id == execution_id,
            WorkflowExecution.org_id == current_user.org_id)\
        .first()

    if not execution:
        raise HTTPException(status_code=404, detail="Not Found")
    
    response = {
        "id": execution.id,
        "status": execution.status,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
        "error_message": execution.error_message,
    }

    return response