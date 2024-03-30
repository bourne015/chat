from typing import Any, List, Dict, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils import log
from api.deps import db_client

router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)


class ChatData(BaseModel):
    '''
    Data structure for User
    '''
    id: int
    user_id: int
    title: Optional[str] = None
    contents: Optional[str] = None


@router.post("/user", name="add user")
async def user_new(user: UserData) -> Any:
    try:
        user_id = db_client.user.add_new_user(
            name=user.name,
            email=user.email,
            phone=user.phone,
            pwd=user.pwd,
            )
    except Exception as err:
        log.debug(f"add user error:{err}")
        return JSONResponse(status_code=500, content=str(e))
    return JSONResponse(status_code=200, content=str(f"added user, id:{user_id}"))


@router.post("/user/{user_id}", name="edit user")
async def user_edit(user_id: int, user: UserData) -> Any:
    try:
        user = db_client.user.update_user_by_id(
            user_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            pwd=user.pwd,
            )
    except Exception as err:
        log.debug(f"edit user error:{err}")
        return JSONResponse(status_code=500, content=str(e))
    return JSONResponse(status_code=200, content=str(f"edited user"))


@router.delete("/user/{user_id}", name="delete user")
async def user_delete(id: int) -> Any:
    try:
        user_id = db_client.user.delete_user(
            user_id=id,
            )
    except Exception as err:
        log.debug(f"delete user error:{err}")
        return JSONResponse(status_code=500, content=str(err))
    return JSONResponse(status_code=200, content=str(f"deleted user_id:{id}"))