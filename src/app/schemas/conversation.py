from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class ConversationBase(BaseModel):
    """Base schema with shared fields."""
    pass  # No input fields required for creation


class Conversation(TimestampSchema, UUIDSchema, PersistentDeletion):
    """Schema representing the full Conversation entity."""
    created_by_user_id: int


class ConversationRead(BaseModel):
    """Schema for reading a conversation."""
    id: int
    uuid: UUID
    created_by_user_id: int
    created_at: datetime
    deleted_at: datetime | None
    is_deleted: bool


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    model_config = ConfigDict(extra="forbid")


class ConversationCreateInternal(ConversationCreate):
    """Internal schema with user mapping for creation."""
    created_by_user_id: int


class ConversationDelete(BaseModel):
    """Schema for soft deleting a conversation."""
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
