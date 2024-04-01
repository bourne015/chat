import time
from typing import Any, List, Dict, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils import log
from api.deps import db_client

router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)


class chatData(BaseModel):
    '''
    Data structure for User
    '''
    id: Optional[int] = None
    title: Optional[str] = None
    model: Optional[str] = None
    contents: Optional[List] = None


@router.post("/user/{user_id}/chat", name="add new chat page")
async def chat_new(user_id: int, chat: chatData) -> Any:
    try:
        created_at = int(time.time())
        updated_at = int(time.time())
        if chat.id == -1:
            chat_id = db_client.chat.add_new_chat(
                title=chat.title,
                contents=chat.contents,
                user_id=user_id,
                model=chat.model,
                created_at=created_at,
                updated_at=updated_at,
                )
            log.debug(f"add chat: {chat_id}")
        else:
            newdata = {}
            if chat.title:
                newdata["title"] = chat.title
            if chat.contents:
                newdata["contents"] = chat.contents
            if chat.model:
                newdata["model"] = chat.model
            newdata["updated_at"] = int(time.time())
            chat_id = db_client.chat.update_chat_by_id(
                chat.id,
                **newdata
                )
            log.debug(f"updated chat: {chat_id}")
    except Exception as err:
        log.debug(f"add chat error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success", "id": chat_id})


@router.post("/user/{user_id}/chats", name="get all chats")
async def get_chats(user_id: int) -> Any:
    try:
        chats = db_client.chat.get_chat_by_user_id(user_id)
    except Exception as err:
        log.debug(f"get chats error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result":"success", "chats": chats})


@router.post("/user/{user_id}/chat/{chat_id}", name="update chat")
async def chat_update(chat: chatData) -> Any:
    try:
        chat = db_client.chat.update_chat_by_id(
            chat_id,
            title=chat.title,
            contents=chat.contents,
            )
    except Exception as err:
        log.debug(f"update chat error:{err}")
        return JSONResponse(status_code=500, content={"result": str(e)})
    return JSONResponse(status_code=200, content={"result": success})


@router.delete("/user/{user_id}/chat/{chat_id}", name="delete chat")
async def chat_delete(chat_id: int) -> Any:
    try:
        user_id = db_client.chat.delete_chat(chat_id=chat_id)
    except Exception as err:
        log.debug(f"delete user error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})