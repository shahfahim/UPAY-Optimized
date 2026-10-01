from fastapi import APIRouter, Request

from hishab.api.schemas import TimeTravelIn

router = APIRouter(prefix="/demo")


@router.post("/time-travel")
def time_travel(body: TimeTravelIn, request: Request):
    return request.app.state.svc.time_travel(body.days)


@router.post("/reset")
def reset(request: Request):
    return request.app.state.svc.reset()
