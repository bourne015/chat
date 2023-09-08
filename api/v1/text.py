from typing import Any, List, Dict
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import StreamingResponse
import json

from utils import chat


router = APIRouter()

class Reqdata(BaseModel):
    model: str
    question: List


@router.post("/chat", name="chat")
async def ask(question: List) -> Any:
    """
    """
    #print("chat len:", len(question))
    print("Q:", question[-1]["content"])
    try:
        answer = chat.asks(question)
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
    # print("Q:", question[-1]["content"])
    def event_generator():
        try:
            answer = chat.asks(question, stream = True)
        except Exception as err:
            yield err
        for text in answer:
            cont = text['choices'][0].get('delta' ,None).get('content', None)
            if cont:
                yield cont

    #return EventSourceResponse(event_generator())
    return  StreamingResponse(event_generator(), media_type="text/event-stream")

