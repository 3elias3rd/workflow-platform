from datetime import datetime
import uuid
from sqlalchemy import DateTime, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.database import Base
from app.core.enums import ActionTypeEnum


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflows.id"), nullable=False, index=True
    )
    type: Mapped[ActionTypeEnum] = mapped_column(
        SQLEnum(ActionTypeEnum), nullable=False
    )
    order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

