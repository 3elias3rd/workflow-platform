from fastapi import HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.db.deps import get_db
from app.core.security import hash_password, create_access_token, verify_password
from app.core.enums import RoleEnum
from app.models import User, Organization, OrgMembership
from app.schemas.auth import TokenResponse, SignupRequest

from sqlalchemy.orm import Session
from sqlalchemy import select

import re


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):

    check_existing(payload.email, payload.organisation_name, db)
    slug = re.sub(r'[^a-z0-9-]', '', payload.organisation_name.lower().replace(' ', '-'))

    hashed_password = hash_password(payload.password)

    new_user = User(email=payload.email, hashed_password=hashed_password)
    new_org = Organization(name=payload.organisation_name, slug=slug)

    try:
        db.add(new_user)
        db.add(new_org)
        db.flush() #populates new_user.id and new_org.id required to create ord_member row

        org_member = OrgMembership(role=RoleEnum.admin, user_id=new_user.id, org_id=new_org.id)
        db.add(org_member)
        db.commit()
    except Exception:
        db.rollback()
        raise

    data = {"user_id": new_user.id, "org_id": new_org.id, "role": org_member.role.value}
    token = create_access_token(data)

    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    org_membership = db.query(OrgMembership).filter(OrgMembership.user_id == user.id).first()
    if not org_membership:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    data = {
        "user_id": user.id,
        "org_id": org_membership.org_id,
        "role": org_membership.role.value
    }
    token = create_access_token(data)

    return {"access_token": token, "token_type": "bearer"}
    

def check_existing(email: str, organization, db: Session):
    existing_email = db.query(User).filter(User.email == email).first()
    existing_org = db.query(Organization).filter(Organization.name == organization).first()

    if existing_email:
        raise HTTPException(status_code=409, detail="Username already registered")
    if existing_org:
        raise HTTPException(status_code=409, detail="Organization already exists")
    
