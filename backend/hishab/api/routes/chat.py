from fastapi import APIRouter, Request

from hishab.api.schemas import ChatIn

router = APIRouter()


@router.post("/users/{uid}/chat")
def chat(uid: str, body: ChatIn, request: Request):
    return request.app.state.svc.chat(uid, body.message)
