"""Health check endpoints"""

from fastapi import APIRouter, Request, HTTPException, status
from datetime import datetime
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    """
    Health check endpoint (no authentication required).

    Returns basic health status and service information.
    """
    return {
        "status": "healthy",
        "service": "agent-control_plane_api",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint (no authentication required)"""
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/detailed")
async def detailed_health_check(request: Request):
    """
    Detailed health check with dependency status.

    Checks connectivity to database, Redis, and Temporal.
    No authentication required for health checks.
    """
    checks = {
        "api": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Try Supabase (new way)
    try:
        from control_plane_api.app.lib.supabase import get_supabase
        client = get_supabase()
        result = client.table("organizations").select("id").limit(1).execute()
        checks["database"] = "healthy"
    except Exception as e1:
        # Fallback to SQLAlchemy (old way)
        try:
            from control_plane_api.app.database import get_db
            from sqlalchemy import text
            db = next(get_db())
            db.execute(text("SELECT 1"))
            checks["database"] = "healthy (legacy)"
        except Exception as e2:
            logger.error("database_health_check_failed", supabase_error=str(e1), sqlalchemy_error=str(e2))
            checks["database"] = f"unhealthy"

    # Check Redis
    try:
        import redis
        from control_plane_api.app.config import settings
        r = redis.from_url(settings.redis_url)
        r.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        checks["redis"] = f"unhealthy: {str(e)}"

    # Check Temporal (just configuration check, not actual connection)
    try:
        from control_plane_api.app.config import settings
        if settings.temporal_host and settings.temporal_namespace:
            checks["temporal"] = "configured"
        else:
            checks["temporal"] = "not configured"
    except Exception as e:
        logger.error("temporal_health_check_failed", error=str(e))
        checks["temporal"] = f"error: {str(e)}"

    # Determine overall status
    checks["status"] = "healthy" if all(
        v in ["healthy", "healthy (legacy)", "configured"]
        for k, v in checks.items()
        if k not in ["timestamp", "status"]
    ) else "degraded"

    return checks
