from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.db.database import async_get_db
from ...schemas.chat import ChatRequest, ChatResponse
from ...services.openai_service import OpenAIService
from ...api.dependencies import get_current_user
from ...schemas.user import UserRead

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
        response = await openai_service.generate_chat_response(
            message=request.message,
            follow_up=request.follow_up
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 