from typing import Any, List
from fastapi import APIRouter
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
    answer = chat.asks(question)
    return answer.choices[0].message.content

