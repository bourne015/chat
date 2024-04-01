from fastapi import APIRouter

from . import text, user, chatdb


api_router = APIRouter()
api_router.include_router(text.router, tags=["Text"])
api_router.include_router(user.router, tags=["User"])
api_router.include_router(chatdb.router, tags=["Chat"])
