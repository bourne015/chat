import time
from typing import Any, List, Dict, Optional, Annotated
from fastapi import APIRouter, Path, Body, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils import log
from api.deps import db_client

router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)


class BotData(BaseModel):
    '''
    Data structure for Bot
    '''
    name: str
    avatar: Optional[str] = None
    description: Optional[str] = None
    prompts: str
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    likes: Optional[int] = None
    public: Optional[bool] = True
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


@router.post("/bot", name="add bot")
async def bot_new(bot: BotData) -> Any:
    try:
        created_at = int(time.time())
        updated_at = int(time.time())
        bot_id = db_client.bot.add_new_bot(
            name=bot.name,
            avatar=bot.avatar,
            description=bot.description,
            prompts=bot.prompts,
            author_id=bot.author_id,
            author_name=bot.author_name,
            likes=0,
            public=bot.public,
            created_at=created_at,
            updated_at=updated_at,
        )
    except Exception as err:
        log.debug(f"add bot error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success", "id":bot_id})


@router.post("/bot/bots", name="get all bot")
async def bot_all() -> Any:
    try:
        bots = db_client.bot.get_all_bots()
    except Exception as err:
        log.debug(f"get bots error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success", "bots": bots})


@router.post("/bot/{bot_id}/info", name="get bot info")
async def bot_info(bot_id: int) -> Any:
    try:
        bot = db_client.bot.get_bot_by_id(bot_id)
    except Exception as err:
        return JSONResponse(status_code=500, content={"result": str(err)})
    if bot is None:
        log.debug(f"bot:{bot_id} not found")
        return JSONResponse(status_code=200, content={"result": "bot not found"})
    res = {
        "result": "success",
        "id": bot.id,
        "name": bot.name,
        "avatar": bot.avatar,
        "description": bot.description,
        "prompts": bot.prompts,
        "author_id": bot.author_id,
        "author_name": bot.author_name,
        "likes": bot.likes,
        "public": bot.public,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    return JSONResponse(status_code=200, content=res)



@router.post("/bot/{bot_id}", name="edit bot")
async def bot_edit(bot_id: int, bot: BotData) -> Any:
    try:
        new_data = {}
        if bot.name:
            new_data["name"] = bot.name
        if bot.avatar:
            new_data["avatar"] = bot.avatar
        if bot.description:
            new_data["description"] = bot.description
        if bot.prompts:
            new_data["prompts"] = bot.prompts
        if bot.author_id:
            new_data["author_id"] = bot.author_id
        if bot.author_name:
            new_data["author_name"] = bot.author_name
        if bot.likes:
            new_data["likes"] = bot.likes
        if bot.public:
            new_data["public"] = bot.public     
        new_data["updated_at"] = int(time.time())
        bot = db_client.bot.update_bot_by_id(
            bot_id,
            **new_data,
            )
    except Exception as err:
        log.debug(f"edit bot error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})


@router.delete("/bot/{bot_id}", name="delete bot")
async def bot_delete(bot_id: int) -> Any:
    try:
        bot_id = db_client.bot.delete_bot(bot_id=bot_id)
    except Exception as err:
        log.debug(f"delete bot error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})
