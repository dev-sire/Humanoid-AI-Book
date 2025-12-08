"""
Health check endpoint.

Provides health status for all backend services.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    services: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check health of all backend services.

    Returns:
        Health status of Qdrant, Postgres, and OpenAI

    Status Codes:
        200: All services healthy
        503: One or more services unavailable
    """
    try:
        rag_service = RAGService()
        services = await rag_service.check_health()

        # Determine overall status
        all_healthy = all(status == "up" for status in services.values())
        overall_status = "healthy" if all_healthy else "degraded"

        if not all_healthy:
            logger.warning(f"Some services unhealthy: {services}")
            raise HTTPException(
                status_code=503,
                detail={"status": overall_status, "services": services},
            )

        return HealthResponse(status=overall_status, services=services)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={"status": "error", "message": str(e)},
        )
