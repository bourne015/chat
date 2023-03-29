from fastapi import APIRouter

from . import text

api_router = APIRouter()
api_router.include_router(text.router, tags=["Text"])
