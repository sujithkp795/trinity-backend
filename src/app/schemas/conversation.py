from datetime import datetime
from typing import Annotated, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class QueryBase(BaseModel):
    query: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class QueryCreate(QueryBase):
    pass


class QueryRead(QueryBase):
    id: UUID


class ConversationBase(BaseModel):
    """Base schema with shared fields."""
    queries: List[dict] = Field(default_factory=list)


class Conversation(TimestampSchema, UUIDSchema, PersistentDeletion):
    """Schema representing the full Conversation entity."""
    created_by_user_id: int


class ConversationRead(BaseModel):
    """Schema for reading a conversation."""
    id: int
    uuid: UUID
    created_by_user_id: int
    queries: List[dict]
    created_at: datetime
    deleted_at: datetime | None
    is_deleted: bool


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    model_config = ConfigDict(extra="forbid")


class ConversationCreateInternal(ConversationCreate):
    """Internal schema with user mapping for creation."""
    created_by_user_id: int
    queries: List[dict] = Field(default_factory=list)


class ConversationDelete(BaseModel):
    """Schema for soft deleting a conversation."""
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
