from fastapi import APIRouter

from . import text, user, chatdb, bot, assistant, tools


api_router = APIRouter()
api_router.include_router(text.router, tags=["Text"])
api_router.include_router(user.router, tags=["User"])
api_router.include_router(chatdb.router, tags=["Chat"])
api_router.include_router(bot.router, tags=["Bot"])
api_router.include_router(assistant.router, tags=["Assistant"])
api_router.include_router(tools.router, tags=["Tools"])
