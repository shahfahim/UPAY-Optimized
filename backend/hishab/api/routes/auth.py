from fastapi import APIRouter, Request

from hishab.api.schemas import LoginIn, RegisterStartIn, RegisterVerifyIn

router = APIRouter(prefix="/auth")


@router.post("/login")
def login(body: LoginIn, request: Request):
    return request.app.state.svc.login(body.mobile, body.pin)


@router.post("/register/start")
def register_start(body: RegisterStartIn, request: Request):
    return request.app.state.svc.register_start(body.mobile)


@router.post("/register/verify")
def register_verify(body: RegisterVerifyIn, request: Request):
    return request.app.state.svc.register_verify(body.mobile, body.otp, body.name, body.pin)
