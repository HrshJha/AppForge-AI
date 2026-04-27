"""AppForge AI – FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db
from app.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # Startup: create DB tables
    init_db()
    yield
    # Shutdown: nothing to clean up for sync SQLite


app = FastAPI(
    title="AppForge AI",
    description="Compiler-grade NL → production-app generation engine",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount V1 API
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

# Root health (convenience)
@app.get("/")
def root():
    return {"service": "appforge-ai", "version": "0.1.0", "docs": "/docs"}
