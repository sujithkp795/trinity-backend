from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to send to the chat API")
    follow_up: Optional[str] = Field(None, description="Optional follow-up question")
    conversation_id: Optional[int] = Field(None, description="ID of the conversation to append this chat to")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the query was updated")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The response from the chat API")
    conversation_id: int = Field(..., description="ID of the conversation this chat belongs to") 