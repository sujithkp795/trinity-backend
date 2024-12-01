from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
from .users import router as users_router
from .chat import router as chat_router
from .conversations import router as conversations_router
from .google_auth import router as google_auth_router

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(users_router)
router.include_router(chat_router)
router.include_router(conversations_router)
router.include_router(google_auth_router)