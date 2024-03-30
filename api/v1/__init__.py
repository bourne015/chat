from fastapi import APIRouter

from . import text
from . import user

api_router = APIRouter()
api_router.include_router(text.router, tags=["Text"])
api_router.include_router(user.router, tags=["User"])
