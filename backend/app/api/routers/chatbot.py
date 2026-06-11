from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.app.services.chatbot_service import handle_chat_message


router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@router.post("/message")
def chat_message(payload: ChatRequest):
    return handle_chat_message(payload.message, payload.session_id)
