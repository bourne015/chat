from typing import Any, List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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

