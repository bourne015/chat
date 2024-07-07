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
    prompts: str
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    likes: Optional[int] = None
    public: Optional[bool] = True
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    # assistant_id: Optional[str] = None
    model: Optional[str] = None
    file_search: Optional[bool] = False
    vector_store_ids: Optional[dict] = {}
    code_interpreter: Optional[bool] = False
    code_interpreter_files: Optional[dict]  = {}
    functions: Optional[dict] = {}
    temperature: Optional[float] = 1.0


@router.post("/bot", name="add bot")
async def bot_new(bot: BotData) -> Any:
    try:
        assistant_id = None
        if bot.model is None:
            bot.model = "gpt-4o"
        if bot.file_search or bot.code_interpreter or bot.functions:
            new_assistant = assistant.create_assistant(
                name=bot.name,
                description=bot.description,
                model=bot.model,
                file_search=bot.file_search,
                vector_store_ids=list(bot.vector_store_ids.keys()),
                code_interpreter=bot.code_interpreter,
                code_interpreter_files=list(bot.code_interpreter_files.values()),
                functions=list(bot.functions.values()),
                temperature=bot.temperature,
            )
            if new_assistant:
                assistant_id = new_assistant.id
        created_at = int(time.time())
        updated_at = int(time.time())
        print("backend bot:", bot)
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
            assistant_id=assistant_id,
            model=bot.model,
            file_search=bot.file_search,
            vector_store_ids=bot.vector_store_ids,
            code_interpreter=bot.code_interpreter,
            code_interpreter_files=bot.code_interpreter_files,
            functions=bot.functions,
            temperature=bot.temperature,
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
        "created_at": bot.created_at,
        "updated_at": bot.updated_at,
        "assistant_id": bot.assistant_id,
        "model": bot.model,
        "file_search": bot.file_search,
        "vector_store_ids": bot.vector_store_ids,
        "code_interpreter": bot.code_interpreter,
        "code_interpreter_files": bot.code_interpreter_files,
        "functions": bot.functions,
        "temperature": bot.temperature,
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
        if bot.public is not None:
            new_data["public"] = bot.public
            print("this is pub:", bot.public)
        new_data["updated_at"] = int(time.time())
        new_data["model"] = bot.model
        new_data["assistant_id"] = bot.assistant_id
        new_data["file_search"] = bot.file_search
        new_data["vector_store_ids"] = bot.vector_store_ids
        new_data["code_interpreter"] = bot.code_interpreter
        new_data["code_interpreter_files"] = bot.code_interpreter_files
        new_data["functions"] = bot.functions
        new_data["temperature"] = bot.temperature

        bot = db_client.bot.update_bot_by_id(
            bot_id,
            **new_data,
            )
    except Exception as err:
        log.debug(f"edit bot error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})


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
    except Exception as err:
        log.debug(f"delete bot error:{err}")
        return JSONResponse(status_code=500, content={"result": str(err)})
    return JSONResponse(status_code=200, content={"result": "success"})
