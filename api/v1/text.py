from typing import Any, List, Dict
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


class ModelPrompt(BaseModel):
    model: str
    question: str

@router.post("/chat", name="chat")
async def ask(data: ModelPrompt) -> Any:
    """
    a single question
    """
    model = data.model
    question = data.question
    log.debug(f"model: {model}, Q: {question}")
    try:
        answer = chat.ask(question, model)
    except Exception as e:
        log.error(f"err: {e}")
        return JSONResponse(status_code=500, content=str(e))
    return JSONResponse(
            status_code=200,
            content=answer.choices[0].message.content
            )

@router.post("/stream/chat", name="stream chat")
async def ask_stream(data: ModelPrompts) -> Any:
    """
    server sent event
    """
    model = data.model
    question = data.question
    if model == "gpt-4-vision-preview":
        log.debug(f"stream: {model}, Q: {question[-1]['content'][0]['text']}")
    else:
        log.debug(f"stream: {model}, Q: {question[-1]['content']}")
    async def event_generator():
        try:
            answer = chat.asks(question, model, stream = True)
            for text in answer:
                if text:
                    yield text
                #await asyncio.sleep(0.01)
        except Exception as err:
            log.debug(err)
            yield err
    return EventSourceResponse(event_generator())
    #return  StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/image", name="image")
async def image(data: ModelPrompt) -> Any:
    """
    generate image
    """
    model = data.model
    question = data.question
    log.debug(f"image model: {model}, Q: {question}")
    #log.debug(f"image model: {model}")
    try:
        answer = chat.gen_image(question, model)
    except Exception as e:
        log.error(f"err: {e}")
        return JSONResponse(status_code=500, content=str(e))
    return JSONResponse(
            status_code=200,
            content=answer.data[0].b64_json
            #content=answer.data[0].url
            )
