"""V1 API router – combines all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.generate import router as generate_router
from app.api.v1.validate import router as validate_router
from app.api.v1.repair import router as repair_router
from app.api.v1.metrics import router as metrics_router

router = APIRouter()

router.include_router(health_router, tags=["health"])
router.include_router(generate_router, tags=["pipeline"])
router.include_router(validate_router, tags=["validation"])
router.include_router(repair_router, tags=["repair"])
router.include_router(metrics_router, tags=["metrics"])
