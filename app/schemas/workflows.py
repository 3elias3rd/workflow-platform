from pydantic import BaseModel, Field
from app.core.enums import TriggerTypeEnum, ActionTypeEnum


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class TriggerCreate(BaseModel):
    type: TriggerTypeEnum
    config: dict


class ActionCreate(BaseModel):
    type: ActionTypeEnum
    order: int = 0
    config: dict