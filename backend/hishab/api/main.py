"""FastAPI app. Run: uvicorn hishab.api.main:create_app --factory --port 8000"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from hishab.config import Settings, get_settings
from hishab.engine.context import UserNotFound


def build_service(settings: Settings):
    from hishab.data.loader import DataRepo
    from hishab.engine.models import load_from
    from hishab.services import Hishab
    from hishab.store.sqlite import Store

    store = Store(settings.db_path)
    store.reset()  # demo state is seeded fresh on every start
    return Hishab(DataRepo.from_dir(settings.data_dir / "serving"), store, load_from(settings.artifacts_dir), settings)


def create_app(settings: Settings | None = None, svc=None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="Hishab API", version="0.1.0",
                  description="AI cash-flow copilot for upay — demo API on synthetic data.")
    app.state.svc = svc or build_service(settings)
    app.state.settings = settings
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.exception_handler(UserNotFound)
    async def _not_found(_: Request, exc: UserNotFound):
        return JSONResponse(status_code=404, content={"detail": "ব্যবহারকারী পাওয়া যায়নি"})

    @app.exception_handler(ValueError)
    async def _value_error(_: Request, exc: ValueError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    from hishab.services_hub import InsufficientFunds

    @app.exception_handler(InsufficientFunds)
    async def _funds(_: Request, exc: InsufficientFunds):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(PermissionError)
    async def _perm(_: Request, exc: PermissionError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": "তথ্য সঠিক নয়", "errors": jsonable_errors(exc)})

    from hishab.api.routes import auth, demo, users
    for r in (users.router, auth.router, demo.router):
        app.include_router(r, prefix="/api")
    for name in ("hub", "savings", "flows", "impact", "chat"):
        try:
            mod = __import__(f"hishab.api.routes.{name}", fromlist=["router"])
            app.include_router(mod.router, prefix="/api")
        except ModuleNotFoundError:
            pass

    @app.get("/api/health")
    def health():
        return {"status": "ok", "llm": bool(settings.llm_enabled), "demo_today": settings.demo_today.isoformat()}

    return app


def jsonable_errors(exc: RequestValidationError) -> list:
    return [{"loc": list(map(str, e.get("loc", []))), "msg": str(e.get("msg", ""))} for e in exc.errors()]
