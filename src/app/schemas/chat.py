from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to send to the chat API")
    follow_up: Optional[str] = Field(None, description="Optional follow-up question")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The response from the chat API") 