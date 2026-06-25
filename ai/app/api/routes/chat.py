from fastapi import APIRouter, Depends

from app.core.security import verify_internal_api_key
from app.schemas.chat import ChatRespondRequest, ChatRespondResponse
from app.services.chat import respond_chat

router = APIRouter(prefix="/chat", dependencies=[Depends(verify_internal_api_key)])


@router.post("/respond/", response_model=ChatRespondResponse)
def chat_respond(payload: ChatRespondRequest):
    return respond_chat(payload)