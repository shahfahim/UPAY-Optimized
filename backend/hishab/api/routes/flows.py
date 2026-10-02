from fastapi import APIRouter, Depends, Request

from hishab.api.deps import require_user

from hishab.api.schemas import CategoryConfirmIn, CategorySuggestIn, RouteIn, SendIn

router = APIRouter(dependencies=[Depends(require_user)])  # every route here is /users/{uid}/…


@router.post("/users/{uid}/category/suggest")
def category_suggest(uid: str, body: CategorySuggestIn, request: Request):
    return request.app.state.svc.category_suggest(uid, body.counterparty_id, body.counterparty_type, body.amount)


@router.post("/users/{uid}/category/confirm")
def category_confirm(uid: str, body: CategoryConfirmIn, request: Request):
    return request.app.state.svc.category_confirm(uid, body.counterparty_id, body.category)


@router.post("/users/{uid}/route")
def route(uid: str, body: RouteIn, request: Request):
    return request.app.state.svc.route(uid, body.amount, body.destination)


@router.post("/users/{uid}/send")
def send(uid: str, body: SendIn, request: Request):
    return request.app.state.svc.send(uid, body.model_dump())
