from fastapi import APIRouter, Depends, Request

from hishab.api.deps import require_user

from hishab.api.schemas import DpsAdviceIn, DpsOpenIn, EmergencyIn, GoalIn, PaisaIn, PocketMoveIn

router = APIRouter(dependencies=[Depends(require_user)])  # every route here is /users/{uid}/…


@router.get("/users/{uid}/savings")
def savings(uid: str, request: Request):
    return request.app.state.svc.savings(uid)


@router.post("/users/{uid}/savings/pockets/{pocket}/move")
def move_pocket(uid: str, pocket: str, body: PocketMoveIn, request: Request):
    return request.app.state.svc.move_pocket(uid, pocket, body.direction, body.amount)


@router.put("/users/{uid}/savings/paisa")
def set_paisa(uid: str, body: PaisaIn, request: Request):
    return request.app.state.svc.set_paisa(uid, body.on)


@router.post("/users/{uid}/goals/plan")
def plan_goal(uid: str, body: GoalIn, request: Request):
    return request.app.state.svc.plan_goal(uid, body.target, body.months, body.pocket)


@router.post("/users/{uid}/dps/advice")
def dps_advice(uid: str, body: DpsAdviceIn, request: Request):
    return request.app.state.svc.dps_advice(uid, body.goal_target)


@router.post("/users/{uid}/dps/open")
def dps_open(uid: str, body: DpsOpenIn, request: Request):
    return request.app.state.svc.dps_open(uid, body.monthly, body.tenure_months)


@router.post("/users/{uid}/emergency/options")
def emergency(uid: str, body: EmergencyIn, request: Request):
    return request.app.state.svc.emergency(uid, body.amount)
