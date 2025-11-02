from fastapi import APIRouter
from datetime import datetime

from app.core import settings, get_logger
from app.models import HealthResponse
from app.services import health_service

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Health check endpoint that verifies the status of all dependencies
    """
    logger.info("Health check requested")
    
    # Get health status of all services
    services = await health_service.get_health_status()
    
    # Determine overall status
    overall_status = health_service.determine_overall_status(services)
    
    # Get uptime
    uptime = health_service.get_uptime()
    
    health_response = HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version=settings.VERSION,
        services=services,
        uptime_seconds=uptime
    )
    
    logger.info(
        "Health check completed",
        status=overall_status.value,
        uptime_seconds=uptime,
        services_count=len(services)
    )
    
    return health_response


@router.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }