"""FastAPI app. Run: uvicorn hishab.api.main:create_app --factory --port 8000"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from hishab.config import Settings, get_settings
from hishab.engine.context import UserNotFound
from hishab.errors import LockedOut, UserError

log = logging.getLogger(__name__)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), geolocation=(self), microphone=(self)",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com; script-src 'self'; connect-src 'self'; "
        "frame-src https://www.google.com; frame-ancestors 'none'"
    ),
}


def build_service(settings: Settings):
    from hishab.data.loader import DataRepo
    from hishab.engine.models import load_from
    from hishab.services import Hishab
    from hishab.store.sqlite import Store

    store = Store(settings.db_path)
    if settings.demo_mode:
        store.reset()  # demo deployments start from fresh seeded state; otherwise state persists
    return Hishab(DataRepo.from_dir(settings.data_dir / "serving"), store, load_from(settings.artifacts_dir), settings)


def _default_web_dist() -> Path:
    from hishab.config import BACKEND_DIR
    return Path(os.environ.get("HISHAB_WEB_DIST", BACKEND_DIR.parent / "web" / "dist"))


def create_app(settings: Settings | None = None, svc=None, web_dist: Path | None = None) -> FastAPI:
    settings = settings or (svc.settings if svc is not None else get_settings())
    app = FastAPI(title="Hishab API", version="0.1.0",
                  description="AI cash-flow copilot for upay — demo API on synthetic data.")
    app.state.svc = svc or build_service(settings)
    app.state.settings = settings
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
                       allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                       allow_headers=["Authorization", "Content-Type"])

    @app.middleware("http")
    async def _security_headers(request: Request, call_next):
        resp = await call_next(request)
        for k, v in SECURITY_HEADERS.items():
            resp.headers.setdefault(k, v)
        return resp

    @app.exception_handler(UserNotFound)
    async def _not_found(_: Request, exc: UserNotFound):
        return JSONResponse(status_code=404, content={"detail": "ব্যবহারকারী পাওয়া যায়নি"})

    @app.exception_handler(LockedOut)
    async def _locked(_: Request, exc: LockedOut):
        return JSONResponse(status_code=429, content={"detail": str(exc)})

    @app.exception_handler(UserError)
    async def _user_error(_: Request, exc: UserError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def _value_error(request: Request, exc: ValueError):  # a bug, not bad input: keep the details in the log
        log.error("unexpected ValueError on %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "কিছু একটা ভুল হয়েছে"})

    from hishab.services_hub import InsufficientFunds

    @app.exception_handler(InsufficientFunds)
    async def _funds(_: Request, exc: InsufficientFunds):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    from hishab.llm.client import RateLimited

    @app.exception_handler(RateLimited)
    async def _rate(_: Request, exc: RateLimited):
        return JSONResponse(status_code=429, content={"detail": str(exc)})

    @app.exception_handler(PermissionError)
    async def _perm(_: Request, exc: PermissionError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": "তথ্য সঠিক নয়", "errors": jsonable_errors(exc)})

    from hishab.api.routes import auth, demo, users
    for r in (users.router, auth.router, demo.router):
        app.include_router(r, prefix="/api")
    for name in ("hub", "savings", "flows", "impact", "chat", "upay_integration", "agents"):
        try:
            mod = __import__(f"hishab.api.routes.{name}", fromlist=["router"])
            app.include_router(mod.router, prefix="/api")
        except ModuleNotFoundError:
            pass

    @app.get("/api/health")
    def health():
        return {"status": "ok", "llm": bool(settings.llm_enabled), "demo_mode": settings.demo_mode,
                "demo_today": settings.demo_today.isoformat()}

    dist = Path(web_dist) if web_dist is not None else _default_web_dist()
    if (dist / "index.html").exists():
        root = dist.resolve()

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            if path.startswith("api/") or path == "api":
                return JSONResponse(status_code=404, content={"detail": "Not Found"})
            target = (root / path).resolve()
            if path and target.is_file() and root in target.parents:
                return FileResponse(target)
            return FileResponse(root / "index.html")  # client-side routes

    return app


def jsonable_errors(exc: RequestValidationError) -> list:
    return [{"loc": list(map(str, e.get("loc", []))), "msg": str(e.get("msg", ""))} for e in exc.errors()]
