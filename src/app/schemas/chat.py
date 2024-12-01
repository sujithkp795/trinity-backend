from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to send to the chat API")
    follow_up: Optional[str] = Field(None, description="Optional follow-up question")
    image_url: Optional[str] = Field(None, description="Optional image URL")
    conversation_id: int = Field(..., description="ID of the conversation to append this chat to")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The response from the chat API")
    conversation_id: int = Field(..., description="ID of the conversation this chat belongs to") 
    query_id: int = Field(..., description="ID of the query this chat belongs to")