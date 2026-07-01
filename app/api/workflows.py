from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user, require_role
from app.schemas.auth import CurrentUser
from app.models.workflows import Workflow
from app.db.deps import get_db
from sqlalchemy.orm import Session
from app.schemas.workflows import WorkflowCreate


router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.get("/")
def get_workflow(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
       workflows = db.query(Workflow).filter(Workflow.org_id == current_user.org_id).all()
       return workflows

@router.post("/")
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(require_role("admin"))):
    new_workflow = Workflow(
        name=workflow.name,
        org_id=current_user.org_id
    )

    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)

    return new_workflow

@router.get("/{workflow_id}")
def workflow_by_id(workflow_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    workflow = db.query(Workflow).filter(Workflow.org_id == current_user.org_id, Workflow.id == workflow_id).first()
    if not workflow:
         raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow