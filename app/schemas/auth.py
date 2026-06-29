from pydantic import BaseModel, Field
from app.core.enums import RoleEnum


class SignupRequest(BaseModel):
    email: str = Field(min_length=5, max_length=100)
    organisation_name: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=30)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=30)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"