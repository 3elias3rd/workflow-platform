from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.triggers import Trigger
from app.models.workflows import Workflow
from app.models.workflow_executions import WorkflowExecution
from app.workers.tasks import execute_workflow
from typing import Annotated

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/{trigger_id}")
def webhook(trigger_id: str, body: Annotated[dict, Body()], db: Session = Depends(get_db)):
    trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()

    if not trigger:
        raise HTTPException(status_code=404, detail="Not Found")
    
    workflow = db.query(Workflow).filter(Workflow.id == trigger.workflow_id).first()

    if not workflow.is_active:
        raise HTTPException(status_code=400, detail="Bad request") 
    
    new_execution = WorkflowExecution(status="pending", trigger_data=body, org_id=workflow.org_id, workflow_id=workflow.id)

    db.add(new_execution)
    db.commit()
    db.refresh(new_execution)

    execute_workflow.delay(new_execution.id)


    return JSONResponse(
        status_code=202,
        content={
            "execution_id": new_execution.id,
            "status": "accepted"
        }
    )

