from fastapi import APIRouter, Depends, Request

from hishab.api.deps import require_user

from hishab.api.schemas import ChatIn

router = APIRouter(dependencies=[Depends(require_user)])  # every route here is /users/{uid}/…


@router.post("/users/{uid}/chat")
def chat(uid: str, body: ChatIn, request: Request):
    return request.app.state.svc.chat(uid, body.message)
