from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.db.database import async_get_db
from ...schemas.chat import ChatRequest, ChatResponse
from ...services.openai_service import OpenAIService
from ...api.dependencies import get_current_user
from ...schemas.user import UserRead
from ...crud.crud_conversations import crud_conversations
from ...schemas.conversation import ConversationRead, QueryCreate, ConversationCreateInternal, QueryUpdate
from datetime import datetime, UTC
from uuid import uuid4

router = APIRouter(tags=["chat"])

# Initialize OpenAI service
openai_service = OpenAIService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> ChatResponse:
    try:
        # Generate response from OpenAI
        response = await openai_service.generate_chat_response(
            message=request.message,
            follow_up=request.follow_up,
            image_url=request.image_url
        )

        # Handle conversation creation or update
        if request.conversation_id:
            # Get existing conversation
            conversation = await crud_conversations.get(
                db=db,
                schema_to_select=ConversationRead,
                id=request.conversation_id,
                created_by_user_id=current_user["id"],
                is_deleted=False
            )
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            conversation_id = request.conversation_id
        else:
            # Create new conversation
            conversation_internal = ConversationCreateInternal(
                created_by_user_id=current_user["id"],
                queries=[]
            )
            conversation = await crud_conversations.create(db=db, object=conversation_internal)
            conversation_id = conversation["id"]

        # Create new query with serialized datetime and identifiers
        query = {
            "id": len(conversation["queries"]) ,  # Auto-incrementing ID
            "uuid": str(uuid4()),  # UUID for the query
            "query": request.message if not request.follow_up else request.follow_up,
            "response": response,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": None,
            "is_affected": None
        }

        # Add query to conversation
        queries = conversation["queries"] + [query]
        await crud_conversations.update(
            db=db,
            id=conversation_id,
            object={"queries": queries}
        )

        return ChatResponse(response=response, conversation_id=conversation_id, query_id=query["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    

@router.patch("/chat/{conversation_id}/query/{query_id}")
async def update_query(
    conversation_id: int,
    query_id: int,
    update_data: QueryUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    try:
        # Get existing conversation
        conversation = await crud_conversations.get(
            db=db,
            schema_to_select=ConversationRead,
            id=conversation_id,
            created_by_user_id=current_user["id"],
            is_deleted=False
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Find the query to update
        queries = conversation["queries"]
        query_index = -1
        
        for i, query in enumerate(queries):
            if query["id"] == query_id:
                query_index = i
                break
                
        if query_index == -1:
            raise HTTPException(status_code=404, detail="Query not found")

        # Update the query
        queries[query_index]["query"] = update_data.query
        queries[query_index]["response"] = update_data.response
        queries[query_index]["updated_at"] = datetime.now(UTC).isoformat()

        # Mark all subsequent queries as affected
        for i in range(query_index + 1, len(queries)):
            queries[i]["is_affected"] = True

        # Update the conversation with modified queries
        await crud_conversations.update(
            db=db,
            id=conversation_id,
            object={"queries": queries}
        )

        return {"message": "Query updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))