from typing import Any, List, Dict, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import StreamingResponse
import json
import asyncio

from utils import chat
from utils import log


router = APIRouter()
log = log.Logger(__name__, clevel=log.logging.DEBUG)

class ModelPrompts(BaseModel):
    model: str
    question: List


class ChatCompletion(BaseModel):
    model: str
    messages: List
    tools: Optional[list] = None


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
        answer = chat.ask(user_id, question, model)
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
            answer = chat.asks(user_id, question, model, stream = True)
            for text in answer:
                if text:
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
        log.debug(f"stream: {model}, Q: {content}")
    elif type(content) == list:
        log.debug(f"stream: {model}, Q: {content[0].get('text')}")
    async def event_generator():
        try:
            answer = chat.completions(user_id, data)
            for text in answer:
                yield text
        except Exception as err:
            log.debug(err)
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
        answer = chat.gen_image(user_id, question, model)
    except Exception as e:
        log.error(f"err: {e}")
        return JSONResponse(status_code=500, content=str(e))
    return JSONResponse(
            status_code=200,
            content=answer.data[0].b64_json
            #content=answer.data[0].url
            )
