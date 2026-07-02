"""
Health and Monitoring Router.

Provides liveness and readiness check endpoints for load balancers
and container orchestrators (Kubernetes/ECS), as well as a metrics endpoint.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis_client
from app.core.config import get_settings
from app.dependencies.database import get_db
from app.schemas.common import ErrorResponse, HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["System Health"],
    responses={
        503: {"model": ErrorResponse, "description": "Service Unavailable"},
    },
)


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Deep health status check",
)
async def health_check(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> HealthResponse:
    """
    Perform checks on database and cache connections.
    Returns status 503 if any core system dependency is down.
    """
    settings = get_settings()

    db_status = "healthy"
    redis_status = "healthy"
    overall_status = "healthy"

    # Verify Database Connectivity
    try:
        from sqlalchemy import text

        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"
        overall_status = "unhealthy"

    # Verify Redis Connectivity
    if settings.CACHE_ENABLED:
        try:
            redis_client = get_redis_client()
            await redis_client.ping()
        except Exception:
            redis_status = "unhealthy"
            # Only mark overall unhealthy if cache is required and down.
            # Fail open or closed depending on requirements.
            overall_status = "unhealthy"
    else:
        redis_status = "disabled"

    if overall_status == "unhealthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT.value,
        components={"database": db_status, "cache": redis_status},
    )


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
)
async def liveness() -> dict[str, str]:
    """
    Minimal sanity check returning 200 OK.
    Confirms the application process is running and responding.
    """
    return {"status": "alive"}


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
)
async def readiness(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Confirms that external network dependencies (DB, Redis) are online
    and ready to receive requests.
    """
    try:
        from sqlalchemy import text

        await db.execute(text("SELECT 1"))
        settings = get_settings()
        if settings.CACHE_ENABLED:
            redis_client = get_redis_client()
            await redis_client.ping()
        return {"status": "ready"}
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready"}
