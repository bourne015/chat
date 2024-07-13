import time
from typing import Any, List, Dict, Optional, Annotated
from fastapi import APIRouter, Path, Body, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils import assistant, log
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
    instructions: Optional[str] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    likes: Optional[int] = None
    public: Optional[bool] = True
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    assistant_id: Optional[str] = None
    model: Optional[str] = None
    file_search: Optional[bool] = False
    vector_store_ids: Optional[dict] = {}
    code_interpreter: Optional[bool] = False
    code_interpreter_files: Optional[dict]  = {}
    functions: Optional[dict] = {}
    temperature: Optional[float] = 1.0

    def to_openai_assistant(self):
        tools = []
        tool_resources = {}
        if self.file_search is True:
            tools.append({"type": "file_search"})
        if self.code_interpreter is True:
            tools.append({"type": "code_interpreter"})
        if self.vector_store_ids:
            tool_resources["file_search"] = {
                "vector_store_ids": list(self.vector_store_ids.keys())
            }
        if self.code_interpreter_files:
            tool_resources["code_interpreter"] = {
                    "file_ids": list(self.code_interpreter_files.values())
            }
        if self.functions:
            functions=list(self.functions.values())
            for x in functions:
                tools.append({"type": "function", "function": x}) 
        op_data = dict(
            name=self.name,
            description=self.description,
            instructions=self.instructions,
            model=self.model,
            tools=tools,
            tool_resources=tool_resources,
            temperature=self.temperature,
        )
        return op_data


@router.post("/bot", name="add bot")
async def bot_new(bot: BotData) -> Any:
    newbot = None
    try:
        assistant_id = None
        if bot.model is None:
            bot.model = "gpt-4o"
        bot_data = bot.dict()
        if bot.file_search or bot.code_interpreter or bot.functions:
            new_assistant = assistant.create_assistant(
                **(bot.to_openai_assistant())
            )
            if new_assistant:
                assistant_id = new_assistant.id
        updated_at = int(time.time())
        bot_data["created_at"] = updated_at
        bot_data["updated_at"] = updated_at
        bot_data["assistant_id"] = assistant_id
        newbot = db_client.bot.add_new_bot(
            **bot_data
        )
        update_shares(updated_at)
    except Exception as err:
        log.debug(f"add bot error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content=newbot)


@router.post("/bot/bots", name="get all bot")
async def bot_all() -> Any:
    bots = None
    shares = None
    try:
        bots = db_client.bot.get_all_bots()
        shares = db_client.shares.get_all_shares()
    except Exception as err:
        log.debug(f"get bots error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(
        status_code=200,
        content={"bots": bots, "date": shares.get("bot_updated")})


@router.post("/bot/{bot_id}/info", name="get bot info")
async def bot_info(bot_id: int) -> Any:
    bot = None
    try:
        bot = db_client.bot.get_bot_by_id(bot_id)
    except Exception as err:
        return JSONResponse(status_code=500, content={"result": str(err)})
    if bot is None:
        log.debug(f"bot:{bot_id} not found")
        return JSONResponse(status_code=200, content={"result": "bot not found"})
    return JSONResponse(status_code=200, content=bot)



@router.post("/bot/{bot_id}", name="edit bot")
async def bot_edit(bot_id: int, bot: BotData) -> Any:
    new_bot = None
    try:
        new_data = bot.dict()
        updated_at = int(time.time())
        new_data["updated_at"] = updated_at
        new_bot = db_client.bot.update_bot_by_id(
            bot_id,
            **new_data,
        )
        update_shares(updated_at)
        if bot.assistant_id:
            assistant.update_assistant(
                bot.assistant_id,
                **(bot.to_openai_assistant()))
        elif bot.file_search or bot.code_interpreter or bot.functions:
            new_assistant = assistant.create_assistant(
                **(bot.to_openai_assistant()))
            if new_assistant:
                assistant_id = new_assistant.id
                new_bot = db_client.bot.update_bot_by_id(
                    bot_id,
                    assistant_id=assistant_id)
    except Exception as err:
        log.debug(f"edit bot error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content=new_bot)


@router.delete("/bot/{bot_id}", name="delete bot")
async def bot_delete(bot_id: int, assistant_id: str) -> Any:
    try:
        del_asst = None
        if assistant_id:
            del_asst = assistant.delete_assistant(assistant_id)
            if del_asst and del_asst.deleted == True:
                db_client.bot.delete_bot(bot_id=bot_id)
        else:
            db_client.bot.delete_bot(bot_id=bot_id)
        update_shares(int(time.time()))
    except Exception as err:
        log.debug(f"delete bot error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})


@router.get("/shares", name="share information")
async def get_shares() -> Any:
    shared = None
    try:
        shared = db_client.shares.get_all_shares()
    except Exception as err:
        log.debug(f"update_shared error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content=shared)


def update_shares(updated_at):
    try:
        shared = db_client.shares.get_all_shares()
        if shared:
            db_client.shares.update_shares_by_id(
                shared["id"],
                bot_updated=updated_at)
    except Exception as err:
        log.debug(f"update_shared error:{err}")
