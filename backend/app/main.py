from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from app.api.routes import auth_router, footprints_router, trips_router, uploads_router
from app.core.errors import AppError, ErrorCode, register_error_handlers
from app.core.logging import configure_logging, request_logging_middleware
from app.core.settings import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from app.db.base import Base
        from app.db.session import engine
        from app.models import Footprint, Trip, User  # noqa: F401

        Base.metadata.create_all(bind=engine)
        yield

    app = FastAPI(title=resolved_settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger = configure_logging(resolved_settings.log_level)
    register_error_handlers(app, logger)
    app.include_router(auth_router)
    app.include_router(trips_router)
    app.include_router(footprints_router)
    app.include_router(uploads_router)

    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        return await request_logging_middleware(request, call_next, logger)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "env": resolved_settings.app_env}

    @app.get("/demo/resource-error")
    def demo_resource_error() -> None:
        raise AppError(
            message="Resource not found.",
            code=ErrorCode.RESOURCE_ERROR,
            status_code=404,
        )

    return app


app = create_app()
