import time
from typing import Any, List, Dict, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils import log
from utils import chat as chatlib
from utils import credit
from api.deps import db_client

router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)


class chatData(BaseModel):
    '''
    Data structure for User
    '''
    id: Optional[int] = None
    page_id: Optional[int] = None
    title: Optional[str] = None
    model: Optional[str] = None
    contents: Optional[List] = None
    assistant_id: Optional[str] = None
    thread_id: Optional[str] = None
    bot_id: Optional[int] = None


@router.post("/user/{user_id}/chat", name="add or edit chat page")
async def chat_new(user_id: int, chat: chatData) -> Any:
    chat_id = -1
    new_chat = False
    try:
        created_at = int(time.time())
        updated_at = int(time.time())
        if chat.id == -1:
            new_chat = True
            chat_id = db_client.chat.add_new_chat(
                title=chat.title,
                contents=chat.contents,
                page_id=chat.page_id,
                user_id=user_id,
                model=chat.model,
                created_at=created_at,
                updated_at=updated_at,
                assistant_id=chat.assistant_id,
                thread_id=chat.thread_id,
                bot_id=chat.bot_id,
                )
            log.debug(f"add chat: {chat_id}")
        else:
            newdata = {}
            newdata["page_id"] = chat.page_id
            if chat.title:
                newdata["title"] = chat.title
            if chat.contents:
                newdata["contents"] = chat.contents
            if chat.model:
                newdata["model"] = chat.model
            if chat.assistant_id:
                newdata["assistant_id"] = chat.assistant_id
            if chat.thread_id:
                newdata["thread_id"] = chat.thread_id
            if chat.bot_id:
                newdata["bot_id"] = chat.bot_id
            newdata["updated_at"] = int(time.time())
            chat_id = db_client.chat.update_chat_by_id(
                chat.id,
                **newdata
                )
            log.debug(f"updated chat: {chat_id}")
    except Exception as err:
        log.debug(f"add chat error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    userinfo = None
    if new_chat and chat.assistant_id is not None:
        userinfo = credit.from_costs(user_id, 0.03) #every code interpreter cost $0.03
    # userinfo = chatlib.credit_balance(user_id, chat, new_chat)
    update_time = userinfo.updated_at if userinfo else int(time.time())
    res = {"result": "success", "id": chat_id, "updated_at": update_time}
    return JSONResponse(status_code=200, content=res)


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
            page_id=chat.page_id,
            title=chat.title,
            contents=chat.contents,
            )
    except Exception as err:
        log.debug(f"update chat error:{err}")
        return JSONResponse(status_code=500, content={"result": str(e)})
    return JSONResponse(status_code=200, content={"result": success})


@router.delete("/user/{user_id}/chat/{chat_id}", name="delete chat")
async def chat_delete(user_id: int, chat_id: int) -> Any:
    try:
        db_client.chat.delete_chat(chat_id=chat_id)
        user_data = {"updated_at": int(time.time())}
        db_client.user.update_user_by_id(
            user_id,
            **user_data,
        )
    except Exception as err:
        log.debug(f"delete user error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    res = {"result": "success", "updated_at": user_data["updated_at"]}
    return JSONResponse(status_code=200, content=res)
