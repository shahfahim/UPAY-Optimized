from fastapi import APIRouter, Depends, Header, Request

from hishab.api.deps import require_session

from hishab.api.schemas import LoginIn, RegisterStartIn, RegisterVerifyIn

router = APIRouter(prefix="/auth")


@router.post("/login")
def login(body: LoginIn, request: Request):
    return request.app.state.svc.login(body.mobile, body.pin, ip=request.client.host if request.client else None)


@router.post("/register/start")
def register_start(body: RegisterStartIn, request: Request):
    return request.app.state.svc.register_start(body.mobile)


@router.post("/register/verify")
def register_verify(body: RegisterVerifyIn, request: Request):
    return request.app.state.svc.register_verify(body.mobile, body.otp, body.name, body.pin)


@router.post("/logout")
def logout(request: Request, _: str = Depends(require_session), authorization: str | None = Header(default=None)):
    return request.app.state.svc.logout((authorization or "").partition(" ")[2].strip())


@router.post("/logout-all")
def logout_all(request: Request, uid: str = Depends(require_session)):
    """Sign this user out on every device (e.g. a lost phone)."""
    return request.app.state.svc.logout_all(uid)
