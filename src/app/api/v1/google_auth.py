from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth import exceptions as google_auth_exceptions
import logging

from ...core.config import settings
from ...core.db.database import async_get_db
from ...core.security import create_access_token, create_refresh_token
from ...crud.crud_users import crud_users
from ...schemas.google_auth import GoogleAuthRequest, GoogleUser
from ...schemas.user import UserCreateInternal, UserRead
from ...core.security import get_password_hash
import secrets

router = APIRouter(tags=["google-auth"])

logger = logging.getLogger(__name__)

@router.post("/auth/google", response_model=dict)
async def google_auth(
    request: GoogleAuthRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    try:
        # Create a Request object for auth transport
        auth_request = requests.Request()

        try:
            # Verify the Google ID token properly
            idinfo = id_token.verify_oauth2_token(
                request.token,
                auth_request,
                settings.GOOGLE_CLIENT_ID
            )
            print(idinfo)

            # Verify issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # Get Google user info
            google_user = GoogleUser(
                email=idinfo["email"],
                name=idinfo.get("name", ""),
                picture=idinfo.get("picture"),
                given_name=idinfo.get("given_name"),
                family_name=idinfo.get("family_name")
            )

        except ValueError as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid token: {str(e)}"
            )

        # Check if user exists
        db_user = await crud_users.get(db=db, email=google_user.email)
        
        if not db_user:
            # Create new user
            username = google_user.email.split("@")[0].replace(".", "") + secrets.token_urlsafe(6).lower()
            random_password = secrets.token_urlsafe(32)
            
            user_data = {
                "email": google_user.email,
                "name": google_user.name,
                "username": username,
                "hashed_password": get_password_hash(random_password),
                "profile_image_url": google_user.picture or settings.DEFAULT_PROFILE_IMAGE
            }
            
            user_internal = UserCreateInternal(**user_data)
            db_user = await crud_users.create(db=db, object=user_internal)
            db_user = db_user.model_dump()

        # Create tokens
        access_token = await create_access_token(data={"sub": db_user["username"]})
        refresh_token = await create_refresh_token(data={"sub": db_user["username"]})

        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        logger.error(f"Unexpected error in Google auth: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
