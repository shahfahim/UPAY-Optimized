from fastapi import APIRouter, Request

from hishab.api.schemas import BudgetIn, RespondIn

router = APIRouter()


@router.get("/users/{uid}/health")
def health(uid: str, request: Request):
    return request.app.state.svc.health(uid)


@router.get("/users/{uid}/lessons")
def lessons(uid: str, request: Request):
    return request.app.state.svc.lessons(uid)


@router.post("/users/{uid}/lessons/{lesson_id}/respond")
def lesson_respond(uid: str, lesson_id: str, body: RespondIn, request: Request):
    return request.app.state.svc.lesson_respond(uid, lesson_id, body.accepted)


@router.get("/users/{uid}/readiness")
def readiness(uid: str, request: Request):
    return request.app.state.svc.readiness(uid)


@router.get("/users/{uid}/levels")
def levels(uid: str, request: Request):
    return request.app.state.svc.levels(uid)


@router.get("/users/{uid}/calendar")
def calendar(uid: str, month: str, request: Request):
    return request.app.state.svc.calendar(uid, month)


@router.get("/users/{uid}/budget")
def budget(uid: str, period: str, request: Request):
    return request.app.state.svc.budget(uid, period)


@router.put("/users/{uid}/budget")
def set_budget(uid: str, body: BudgetIn, request: Request):
    return request.app.state.svc.set_budget(uid, body.mode, body.manual)


@router.get("/users/{uid}/transactions")
def transactions(uid: str, request: Request, limit: int = 50):
    return request.app.state.svc.transactions(uid, limit)
