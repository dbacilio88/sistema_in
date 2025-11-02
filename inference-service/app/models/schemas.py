from pydantic import BaseModel
from typing import Dict, Any, Optional
from enum import Enum


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class ServiceHealth(BaseModel):
    status: ServiceStatus
    details: Optional[Dict[str, Any]] = None
    response_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    status: ServiceStatus
    timestamp: str
    version: str
    services: Dict[str, ServiceHealth]
    uptime_seconds: float


class StreamStartRequest(BaseModel):
    camera_id: str
    rtsp_url: str
    zone_id: Optional[str] = None
    enable_detection: bool = True
    enable_tracking: bool = True


class StreamStartResponse(BaseModel):
    success: bool
    message: str
    stream_id: Optional[str] = None
    camera_id: str


class StreamStatusResponse(BaseModel):
    stream_id: str
    camera_id: str
    status: str  # "running", "stopped", "error"
    fps: Optional[float] = None
    frames_processed: int = 0
    last_frame_timestamp: Optional[str] = None
    error_message: Optional[str] = None