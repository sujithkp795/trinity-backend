from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user
from ...core.db.database import async_get_db
from ...crud.crud_conversations import crud_conversations
from ...crud.crud_users import crud_users
from ...schemas.conversation import ConversationCreateInternal, ConversationRead, ConversationDelete, QueryCreate
from ...schemas.user import UserRead
from datetime import datetime, UTC

router = APIRouter(tags=["conversations"])


@router.post("/conversations", response_model=ConversationRead, status_code=201)
async def create_conversation(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> ConversationRead:
    """
    Creates a new conversation for the authenticated user.
    """
    conversation_internal = ConversationCreateInternal(
        created_by_user_id=current_user["id"],
        queries=[]  # Initialize with empty list instance
    )
    created_conversation: ConversationRead = await crud_conversations.create(db=db, object=conversation_internal)
    return created_conversation


# @from fastapi import HTTPException
from typing import List

@router.get("/conversations", response_model=List[ConversationRead])
async def get_conversations(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> List[ConversationRead]:
    """
    Retrieves all conversations created by the authenticated user.
    """
    # Fetch the conversations
    conversations = await crud_conversations.get_multi(
        db=db, schema_to_select=ConversationRead, created_by_user_id=current_user["id"], is_deleted=False
    )

    # Ensure we're returning a list of conversations
    if isinstance(conversations, dict) and 'data' in conversations:
        return conversations['data']

    # If no conversations are found, return an empty list
    if not conversations:
        return []

    return conversations



@router.get("/conversations/{id}", response_model=ConversationRead)
async def get_conversation(
    id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> ConversationRead:
    """
    Retrieves a single conversation by ID for the authenticated user.
    """
    conversation = await crud_conversations.get(
        db=db, schema_to_select=ConversationRead, id=id, created_by_user_id=current_user["id"], is_deleted=False
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{id}", status_code=204)
async def delete_conversation(
    id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> None:
    """
    Soft-deletes a conversation by ID for the authenticated user.
    """
    conversation = await crud_conversations.get(
        db=db, schema_to_select=ConversationRead, id=id, created_by_user_id=current_user["id"], is_deleted=False
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    delete_schema = ConversationDelete(is_deleted=True, deleted_at=datetime.now(UTC))
    await crud_conversations.update(db=db, id=id, object=delete_schema)


@router.post("/conversations/{id}/queries", response_model=ConversationRead)
async def add_query_to_conversation(
    id: int,
    query: QueryCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> ConversationRead:
    """
    Adds a new query to an existing conversation.
    """
    conversation = await crud_conversations.get(
        db=db, schema_to_select=ConversationRead, id=id, created_by_user_id=current_user["id"], is_deleted=False
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Create new query object with UUID
    new_query = {
        "id": str(uuid4()),
        "query": query.query,
        "created_at": datetime.now(UTC).isoformat()
    }
    
    # Get existing queries and append new one
    existing_queries = conversation["queries"]
    existing_queries.append(new_query)
    
    # Update conversation with new queries list
    update_data = {"queries": existing_queries}
    await crud_conversations.update(db=db, id=id, object=update_data)
    
    # Get and return updated conversation
    updated_conversation = await crud_conversations.get(
        db=db, schema_to_select=ConversationRead, id=id, created_by_user_id=current_user["id"], is_deleted=False
    )
    return updated_conversation
