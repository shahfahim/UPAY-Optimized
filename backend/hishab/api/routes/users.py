from fastapi import APIRouter, Depends, Request

from hishab.api.deps import require_demo_mode, require_user

from hishab.api.schemas import RespondIn, SimulateIn

router = APIRouter()
auth = [Depends(require_user)]


def svc(request: Request):
    return request.app.state.svc


@router.get("/users", dependencies=[Depends(require_demo_mode)])
def users(request: Request):  # seeded synthetic demo users only
    return svc(request).users()


@router.get("/users/{uid}/home", dependencies=auth)
def home(uid: str, request: Request):
    return svc(request).home(uid)


@router.get("/users/{uid}/shell", dependencies=auth)
def shell(uid: str, request: Request):
    return svc(request).shell(uid)


@router.get("/users/{uid}/notifications", dependencies=auth)
def notifications(uid: str, request: Request):
    return svc(request).notifications(uid)


@router.post("/users/{uid}/actions/simulate", dependencies=auth)
def simulate(uid: str, body: SimulateIn, request: Request):
    return svc(request).simulate(uid, body.action_id)


@router.post("/users/{uid}/actions/{action_id}/respond", dependencies=auth)
def respond(uid: str, action_id: str, body: RespondIn, request: Request):
    return svc(request).respond(uid, "action", action_id, body.accepted)
