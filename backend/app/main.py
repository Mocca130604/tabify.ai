"""Main FastAPI application for Tabify.ai."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

_app_dir = Path(__file__).resolve().parent
_backend_dir = _app_dir.parent
_repo_root = _backend_dir.parent
for _p in [str(_repo_root), str(_backend_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from backend.app.config import settings
from backend.app.routers import health, inspect, predict
from backend.app.ml.tabpfn_engine import tabpfn_engine

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("tabify")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown hooks."""
    logger.info("==================================================")
    logger.info("      Tabify.ai - Local TabPFN Foundation Engine")
    logger.info(f"   TabPFN Version: {tabpfn_engine.get_version()}")
    logger.info(f"   Target Device:  {tabpfn_engine.device}")
    logger.info(f"   Weights Cached: {tabpfn_engine.is_model_cached()}")
    logger.info("==================================================")
    yield
    logger.info("Shutting down Tabify.ai backend.")


app = FastAPI(
    title="Tabify.ai API",
    description="Local tabular foundation model dashboard powered by TabPFN (Prior Labs)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Structured Error Handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Normalize HTTPExceptions into standard structured format."""
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": detail.get("error_code", "HTTP_ERROR"),
                "message": detail.get("message", "An HTTP error occurred"),
                "hint": detail.get("hint"),
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": f"HTTP_{exc.status_code}",
            "message": str(detail),
            "hint": None,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler ensuring no stack trace leaks to client."""
    logger.exception(f"Unhandled server exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request.",
            "hint": "Check backend console logs for detailed diagnostics.",
        },
    )


# Register Routers
app.include_router(health.router)
app.include_router(inspect.router)
app.include_router(predict.router)


@app.get("/")
def root():
    """Root redirect / discovery ping."""
    return {
        "project": "Tabify.ai",
        "description": "Local TabPFN tabular foundation model API",
        "docs": "/docs",
        "health": "/api/health",
    }
