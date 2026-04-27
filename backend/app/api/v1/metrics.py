"""GET /metrics – aggregate pipeline metrics."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import CompileJob

router = APIRouter()


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """Return aggregate benchmark/pipeline metrics."""
    total = db.query(func.count(CompileJob.id)).scalar() or 0
    success = db.query(func.count(CompileJob.id)).filter(CompileJob.status == "success").scalar() or 0
    avg_latency = db.query(func.avg(CompileJob.latency_ms)).filter(CompileJob.latency_ms.isnot(None)).scalar()
    avg_repairs = db.query(func.avg(CompileJob.repair_count)).scalar()
    avg_cost = db.query(func.avg(CompileJob.token_cost_usd)).scalar()

    return {
        "total_compiles": total,
        "success_count": success,
        "success_rate": round(success / total, 2) if total > 0 else 0.0,
        "avg_latency_ms": round(avg_latency or 0, 1),
        "avg_repair_count": round(avg_repairs or 0, 2),
        "avg_cost_usd": round(avg_cost or 0, 4),
    }
