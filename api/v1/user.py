import time
from typing import Any, List, Dict, Optional, Annotated
from fastapi import APIRouter, Path, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from utils import log
from api.deps import db_client
from core.security import get_password_hash, verify_password

router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)


class UserData(BaseModel):
    '''
    Data structure for User
    '''
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    pwd: Optional[str] = None
    avatar: Optional[str] = None
    active: Optional[bool] = True


@router.post("/user", name="add user")
async def user_new(user: UserData) -> Any:
    try:
        olduser = db_client.user.get_user_by_email(user.email)
        if olduser:
            return JSONResponse(status_code=200, content={"result": "user already exists"})
        hash_pwd = get_password_hash(user.pwd)
        created_at = int(time.time())
        updated_at = int(time.time())
        user_id = db_client.user.add_new_user(
            name=user.name,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            pwd=hash_pwd,
            created_at=created_at,
            updated_at=updated_at,
            )
    except Exception as err:
        log.debug(f"add user error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success", "id":user_id})


@router.post("/user/login", name="get user by mail")
async def user_get(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Any:
    try:
        db_user = db_client.user.get_user_by_email(form_data.username)
    except Exception as err:
        log.debug(f"get user error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    if not db_user:
        return JSONResponse(status_code=200, content={"result": "user not found"})
    if not verify_password(form_data.password, db_user.pwd):
        return JSONResponse(status_code=200, content={"result": "wrong password"})
    res = {
        "result": "success",
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "phone": db_user.phone,
        "avatar": db_user.avatar,
    }
    return JSONResponse(status_code=200, content=res)


@router.post("/user/{user_id}", name="edit user")
async def user_edit(user_id: int, user: UserData) -> Any:
    try:
        new_data = {}
        if user.name:
            new_data["name"] = user.name
        if user.email:
            new_data["email"] = user.email
        if user.phone:
            new_data["phone"] = user.phone
        if user.avatar:
            new_data["avatar"] = user.avatar
        new_data["updated_at"] = int(time.time())       
        user = db_client.user.update_user_by_id(
            user_id,
            **new_data,
            )
    except Exception as err:
        log.debug(f"edit user error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})


@router.delete("/user/", name="delete user")
async def user_delete(id: int) -> Any:
    try:
        user_id = db_client.user.delete_user(
            user_id=id,
            )
    except Exception as err:
        log.debug(f"delete user error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})
