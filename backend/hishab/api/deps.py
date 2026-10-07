"""Request dependencies shared by the routers."""

from __future__ import annotations

from fastapi import Header, HTTPException, Request


def require_session(request: Request, authorization: str | None = Header(default=None)) -> str:
    """Any logged-in user (`Authorization: Bearer …`); returns their user id."""
    scheme, _, token = (authorization or "").partition(" ")
    owner = request.app.state.svc.store.session_user(token.strip()) if scheme.lower() == "bearer" and token else None
    if owner is None:
        raise HTTPException(status_code=401, detail="আবার লগইন করুন")
    return owner


def require_demo_mode(request: Request) -> None:
    """Demo-only routes do not exist unless HISHAB_DEMO_MODE=1."""
    if not request.app.state.settings.demo_mode:
        raise HTTPException(status_code=404, detail="Not Found")


def require_user(uid: str, request: Request, authorization: str | None = Header(default=None)) -> str:
    """The session token must belong to the user in the path."""
    if require_session(request, authorization) != uid:
        raise HTTPException(status_code=403, detail="এই অ্যাকাউন্ট দেখার অনুমতি নেই")
    return uid
