from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user, require_role
from app.schemas.auth import CurrentUser
from app.models.workflows import Workflow
from app.models.triggers import Trigger
from app.db.deps import get_db
from sqlalchemy.orm import Session
from app.schemas.workflows import TriggerCreate

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/{workflow_id}/triggers")
def list_triggers(workflow_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.org_id == current_user.org_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail = "Not found")
    
    triggers = db.query(Trigger).filter(Trigger.workflow_id == workflow.id).all()

    return triggers


@router.post("/{workflow_id}/triggers")
def create_trigger(trigger: TriggerCreate, workflow_id: str, current_user: CurrentUser = Depends(require_role("admin")), db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.org_id == current_user.org_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="Not found")
        
    new_trigger = Trigger(
        workflow_id=workflow_id,
        type=trigger.type,
        config=trigger.config
    )

    db.add(new_trigger)
    db.commit()
    db.refresh(new_trigger)

    return new_trigger