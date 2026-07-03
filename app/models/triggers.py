from datetime import datetime
import uuid
from sqlalchemy import DateTime, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.database import Base
from app.core.enums import TriggerTypeEnum


class Trigger(Base):
    __tablename__ = "triggers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflows.id"), nullable=False, index=True
    )
    type: Mapped[TriggerTypeEnum] = mapped_column(
        SQLEnum(TriggerTypeEnum), nullable=False
    )
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )