from typing import Any, List, Dict, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import StreamingResponse
import json
import asyncio
import logging

from utils import chat


router = APIRouter()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ModelPrompts(BaseModel):
    model: str
    question: List


class ChatCompletion(BaseModel):
    model: str
    messages: List
    tools: Optional[list] = None
    temperature: Optional[float] = None


class ModelPrompt(BaseModel):
    model: str
    question: str

@router.post("/chat", name="chat")
async def ask(data: ModelPrompt, user_id: int) -> Any:
    """
    a single question
    """
    model = data.model
    question = data.question
    #log.debug(f"model: {model}, Q: {question}")
    try:
        answer = await chat.ask(user_id, question, model)
    except Exception as e:
        log.error(f"err: {e}")
        return JSONResponse(status_code=500, content=str(e))
    return JSONResponse(
            status_code=200,
            content=answer
            )

@router.post("/stream/chat", name="stream chat")
async def ask_stream(data: ModelPrompts, user_id: int) -> Any:
    """
    server sent event
    """
    model = data.model
    question = data.question
    content = question[-1].get('content') if question else None
    if type(content) == str:
        log.debug(f"stream: {model}, Q: {content}")
    elif type(content) == list:
        log.debug(f"stream: {model}, Q: {content[0].get('text')}")
    async def event_generator():
        try:
            async for text in await chat.asks(user_id, question, model, stream = True):
                yield text
                #await asyncio.sleep(0.01)
        except Exception as err:
            log.debug(err)
            yield err
    return EventSourceResponse(event_generator())
    #return  StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/stream/chats", name="stream chat")
async def asks_stream(data: ChatCompletion, user_id: int) -> Any:
    """
    server sent event
    """
    model = data.model
    question = data.messages
    tools = data.tools
    content = question[-1].get('content') if question else None
    if type(content) == str:
        log.info(f"stream: {model}, Q: {content}")
    elif type(content) == list:
        log.info(f"stream: {model}, Q: {content[0].get('text')}")
    async def event_generator():
        try:
            async for text in await chat.completions(user_id, data):
                yield text
        except Exception as err:
            log.error(f"Unexpected error: {err}")
            yield err
    return EventSourceResponse(event_generator())
    #return  StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/image", name="image")
async def image(data: ModelPrompt, user_id: int) -> Any:
    """
    generate image
    """
    model = data.model
    question = data.question
    log.debug(f"image model: {model}, Q: {question}")
    #log.debug(f"image model: {model}")
    try:
        answer = await chat.gen_image(user_id, question, model)
    except Exception as e:
        log.error(f"err: {e}")
        return JSONResponse(status_code=500, content=str(e))
    return JSONResponse(
            status_code=200,
            content=answer.data[0].b64_json
            #content=answer.data[0].url
            )
