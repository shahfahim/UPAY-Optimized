"""Request dependencies shared by the routers."""

from __future__ import annotations

from fastapi import Header, HTTPException, Request


def require_user(uid: str, request: Request, authorization: str | None = Header(default=None)) -> str:
    """The session token (`Authorization: Bearer …`) must belong to the user in the path."""
    scheme, _, token = (authorization or "").partition(" ")
    owner = request.app.state.svc.store.session_user(token.strip()) if scheme.lower() == "bearer" and token else None
    if owner is None:
        raise HTTPException(status_code=401, detail="আবার লগইন করুন")
    if owner != uid:
        raise HTTPException(status_code=403, detail="এই অ্যাকাউন্ট দেখার অনুমতি নেই")
    return uid
