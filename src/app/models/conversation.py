import uuid as uuid_pkg
from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey, String, Boolean, ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from ..core.db.database import Base

class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, unique=True, nullable=False)
    queries: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Add any additional fields as needed
