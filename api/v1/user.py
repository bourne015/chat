import time
from typing import Any, List, Dict, Optional, Annotated
from fastapi import APIRouter, Path, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from utils import log
from api.deps import db_client
from core.security import get_password_hash, verify_password, oss

router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)


class UpdatePassword(BaseModel):
    current_password: str
    new_password: str


class UserData(BaseModel):
    '''
    Data structure for User
    '''
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    pwd: Optional[str] = None
    avatar: Optional[str] = None
    credit: Optional[float] = 0.0
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
            credit=user.credit,
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
        "credit": db_user.credit,
        "updated_at": db_user.updated_at,
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
        if user.credit:
            new_data["credit"] = user.credit
        new_data["updated_at"] = int(time.time())
        user = db_client.user.update_user_by_id(
            user_id,
            **new_data,
            )
    except Exception as err:
        log.debug(f"edit user error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})


@router.post("/user/{user_id}/info", name="get user info")
async def user_info(user_id: int) -> Any:
    try:
        db_user = db_client.user.get_user_by_id(user_id)
    except Exception as err:
        return JSONResponse(status_code=500, content={"result": str(err)})
    if db_user is None:
        log.debug(f"user:{user_id} not found")
        return JSONResponse(status_code=200, content={"result": "user not found"})
    res = {
        "result": "success",
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "phone": db_user.phone,
        "avatar": db_user.avatar,
        "credit": db_user.credit,
        "updated_at": db_user.updated_at,
    }
    return JSONResponse(status_code=200, content=res)


@router.post("/user/{user_id}/security", name="change user password")
async def user_chgpwd(user_id: int, form_data: UpdatePassword) -> Any:
    try:
        new_data = {}
        dbuser = db_client.user.get_user_by_id(user_id)
        if not verify_password(form_data.current_password, dbuser.pwd):
            return JSONResponse(status_code=200, content={"result": "wrong password"})
        new_data["pwd"] = get_password_hash(form_data.new_password)
        new_data["updated_at"] = int(time.time())
        user = db_client.user.update_user_by_id(
            user_id,
            **new_data,
            )
    except Exception as err:
        log.debug(f"change user pwd error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})


@router.post("/user/{user_id}/oss_credentials", name="get oss credentials")
def user_oss_credentials(user_id: int) ->Any:
    # need check user first
    cred = oss.get_credentials()
    log.debug(f"user_oss_credentials")
    if cred is None:
        return JSONResponse(status_code=500, content={"result": "failed"})
    return JSONResponse(status_code=200, content={"result": "success", "credentials": cred.to_map()})

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


@router.post("/users", name="get all users")
async def get_all_users() -> Any:
    try:
        users = db_client.user.get_all_users()
    except Exception as err:
        log.debug(f"get all users error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success", "users": users})


@router.post("/user/charge/{user_id}", name="charge for user")
async def user_edit(user_id: int, account: float) -> Any:
    try:
        db_user = db_client.user.get_user_by_id(user_id)
        new_data = {}
        if db_user.credit:
            new_data["credit"] = db_user.credit + account
        else:
            new_data["credit"] = account
        new_data["updated_at"] = int(time.time())
        user = db_client.user.update_user_by_id(
            user_id,
            **new_data,
            )
    except Exception as err:
        log.debug(f"edit user error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})
