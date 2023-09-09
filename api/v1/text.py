from typing import Any, List, Dict
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import StreamingResponse
import json
import asyncio

from utils import chat


router = APIRouter()

class Reqdata(BaseModel):
    model: str
    question: List


@router.post("/chat", name="chat")
async def ask(data: Reqdata) -> Any:
    """
    """
    #print("chat len:", len(question))
    #print("Q:", question[-1]["content"])
    model = data.model
    question = data.question
    # print(f"model: {model}, Q: {question[-1]['content']}")
    try:
        answer = chat.asks(question, model)
    except Exception as e:
        print("err:", e)
        return JSONResponse(status_code=500, content=str(e))

    return JSONResponse(status_code=200, content=answer)

@router.post("/stream/chat", name="stream chat")
async def ask_stream(data: Reqdata) -> Any:
    """
    server sent event
    """
    model = data.model
    question = data.question
    # print(f"model: {model}, Q: {question[-1]['content']}")
    async def event_generator():
        try:
            answer = chat.asks(question, model, stream = True)
        except Exception as err:
            yield err
        for text in answer:
            cont = text['choices'][0].get('delta' ,None).get('content', None)
            if cont:
                yield cont
                await asyncio.sleep(0.01)

    return EventSourceResponse(event_generator())
    #return  StreamingResponse(event_generator(), media_type="text/event-stream")

