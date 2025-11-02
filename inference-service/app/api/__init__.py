from fastapi import APIRouter
from .health import router as health_router
from .inference import router as inference_router
from .websocket import router as websocket_router

router = APIRouter()

# Include all API routes
router.include_router(health_router, tags=["health"])
router.include_router(inference_router, prefix="/inference", tags=["inference"])
router.include_router(websocket_router, tags=["websocket"])

# Future routers will be added here:
# router.include_router(stream_router, prefix="/stream", tags=["stream"])