from fastapi import APIRouter, Depends, Request

from hishab.api.deps import require_session
from hishab.api.schemas import TimeTravelIn

router = APIRouter(prefix="/demo", dependencies=[Depends(require_session)])  # shared clock: logged-in users only


@router.post("/time-travel")
def time_travel(body: TimeTravelIn, request: Request):
    return request.app.state.svc.time_travel(body.days)


@router.post("/reset")
def reset(request: Request):
    return request.app.state.svc.reset()
