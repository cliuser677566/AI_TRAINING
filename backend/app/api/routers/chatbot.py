from fastapi import APIRouter, Header, Request
from pydantic import BaseModel
from typing import Optional

from backend.app.core.config import CHATBOT_SQL_DEBUG_ENABLED, CHATBOT_SQL_DEBUG_TOKEN
from backend.app.services.observability import client_ip_from_headers, resolve_user_from_auth_header
from backend.app.services.chatbot_service import handle_chat_message


router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    debug_sql: bool = False


@router.post("/message")
def chat_message(payload: ChatRequest, request: Request, x_chatbot_debug_token: Optional[str] = Header(default=None)):
    debug_allowed = (
        payload.debug_sql
        and CHATBOT_SQL_DEBUG_ENABLED
        and bool(CHATBOT_SQL_DEBUG_TOKEN)
        and x_chatbot_debug_token == CHATBOT_SQL_DEBUG_TOKEN
    )
    user_id = resolve_user_from_auth_header(request.headers.get("authorization"))
    client_ip = client_ip_from_headers(request.headers.get("x-forwarded-for"), request.client.host if request.client else None)
    return handle_chat_message(
        payload.message,
        payload.session_id,
        include_sql_debug=debug_allowed,
        user_id=user_id,
        client_ip=client_ip,
    )
