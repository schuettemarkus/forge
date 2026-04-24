from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth, health, opportunities, printers, trends, scoring
from app.routers import settings as settings_router

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.ENV == "development"
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    ),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup validation
    if settings.ENV != "development" and settings.SECRET_KEY == "change-me-in-production":
        raise RuntimeError("SECRET_KEY must be changed in production!")
    logger.info("forge.api.starting", version="0.1.0", env=settings.ENV)
    yield
    logger.info("forge.api.shutdown")


app = FastAPI(
    title="Forge API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Global exception handler — never leak stack traces
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
app.include_router(printers.router, prefix="/printers", tags=["printers"])
app.include_router(settings_router.router, prefix="/settings", tags=["settings"])
app.include_router(trends.router, prefix="/trends", tags=["trends"])
app.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
