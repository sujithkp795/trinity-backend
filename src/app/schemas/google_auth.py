from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class GoogleAuthRequest(BaseModel):
    token: str = Field(..., description="ID token from Google OAuth")
    
class GoogleUser(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    locale: Optional[str] = None
