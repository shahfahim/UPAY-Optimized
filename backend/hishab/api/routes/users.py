from fastapi import APIRouter, Request

from hishab.api.schemas import RespondIn, SimulateIn

router = APIRouter()


def svc(request: Request):
    return request.app.state.svc


@router.get("/users")
def users(request: Request):
    return svc(request).users()


@router.get("/users/{uid}/home")
def home(uid: str, request: Request):
    return svc(request).home(uid)


@router.get("/users/{uid}/shell")
def shell(uid: str, request: Request):
    return svc(request).shell(uid)


@router.get("/users/{uid}/notifications")
def notifications(uid: str, request: Request):
    return svc(request).notifications(uid)


@router.post("/users/{uid}/actions/simulate")
def simulate(uid: str, body: SimulateIn, request: Request):
    return svc(request).simulate(uid, body.action_id)


@router.post("/users/{uid}/actions/{action_id}/respond")
def respond(uid: str, action_id: str, body: RespondIn, request: Request):
    return svc(request).respond(uid, "action", action_id, body.accepted)
