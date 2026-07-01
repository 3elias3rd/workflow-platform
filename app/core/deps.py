from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.schemas.auth import CurrentUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> CurrentUser:
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="User is not authenticated")

    return CurrentUser(
        user_id=payload["user_id"],
        org_id=payload["org_id"],
        role=payload["role"]
    )

def require_role(required_role: str):
    def user(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role.value != required_role:
            raise HTTPException(status_code=403, detail="Forbidden request")
        return current_user
    return user
