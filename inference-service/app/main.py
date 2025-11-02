from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core import settings, configure_logging, get_logger
from app.api import router as api_router

# Configure logging first
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Traffic Inference Service", version=settings.VERSION)
    
    # Initialize ML models
    try:
        from app.services.model_service import model_service
        logger.info("Initializing ML models...")
        await model_service.initialize()
        logger.info("ML models initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ML models: {str(e)}")
        logger.warning("Service will start but ML features may not work correctly")
    
    logger.info("Service startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Traffic Inference Service")
    try:
        from app.services.model_service import model_service
        model_service.shutdown()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
    logger.info("Service shutdown completed")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Microservice for traffic violation detection and video stream processing",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app


# Create the FastAPI app instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower(),
    )