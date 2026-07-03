from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user, require_role
from app.schemas.auth import CurrentUser
from app.models.workflows import Workflow
from app.models.actions import Action
from app.db.deps import get_db
from sqlalchemy.orm import Session
from app.schemas.workflows import ActionCreate

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/{workflow_id}/actions")
def list_actions(workflow_id: str, current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.org_id == current_user.org_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail = "Not found")
    
    actions = db.query(Action).filter(Action.workflow_id == workflow.id).order_by(Action.order.asc()).all()

    return actions
     

@router.post("/{workflow_id}/actions")
def create_action(action: ActionCreate, workflow_id: str, current_user: CurrentUser = Depends(require_role("admin")), db: Session = Depends(get_db)):

    workflow = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.org_id == current_user.org_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Not found")
    
    new_action = Action(
        workflow_id=workflow_id,
        type=action.type,
        order=action.order,
        config=action.config
    )

    db.add(new_action)
    db.commit()
    db.refresh(new_action)

    return new_action
