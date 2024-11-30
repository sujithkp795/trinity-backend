from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings


def setup_cors(app: FastAPI) -> None:
    """Setup CORS middleware for the application."""
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=["*"] if settings.CORS_ORIGINS == ["*"] else settings.CORS_ORIGINS,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"] if not settings.CORS_METHODS else settings.CORS_METHODS,
        allow_headers=["*"] if settings.CORS_HEADERS == ["*"] else settings.CORS_HEADERS,
    ) 

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with specific origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods including OPTIONS
#     allow_headers=["*"],
# )

# # ... rest of your code ...