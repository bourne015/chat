from typing import Any, List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import StreamingResponse
import json

from utils import chat


router = APIRouter()

class Question(BaseModel):
    role: str
    content: str


@router.post("/chat", name="chat")
async def ask(question: List) -> Any:
    """
    """
    #print("chat len:", len(question))
    #print("Q:", question[-1]["content"])
    try:
        answer = chat.asks(question)
    except Exception as e:
        print("err:", e)
        return JSONResponse(status_code=500, content=str(e))

    return JSONResponse(status_code=200, content=answer)

@router.post("/stream/chat", name="stream chat")
async def ask_stream(question: List) -> Any:
    """
    server sent event
    """
    # print("Q:", question[-1]["content"])
    def event_generator():
        answer = chat.asks(question, stream = True)
        for text in answer:
            cont = text['choices'][0].get('delta' ,None).get('content', None)
            if cont:
                yield cont

    #return EventSourceResponse(event_generator())
    return  StreamingResponse(event_generator(), media_type="text/event-stream")

