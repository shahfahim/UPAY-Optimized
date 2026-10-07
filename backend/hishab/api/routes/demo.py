from fastapi import APIRouter, Depends, Request

from hishab.api.deps import require_demo_mode, require_session
from hishab.api.schemas import TimeTravelIn

# Shared clock and global reset: demo deployments only, and only for logged-in users.
router = APIRouter(prefix="/demo", dependencies=[Depends(require_demo_mode), Depends(require_session)])


@router.post("/time-travel")
def time_travel(body: TimeTravelIn, request: Request):
    return request.app.state.svc.time_travel(body.days)


@router.post("/reset")
def reset(request: Request):
    return request.app.state.svc.reset()
