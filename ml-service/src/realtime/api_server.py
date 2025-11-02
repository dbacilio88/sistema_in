"""
FastAPI server for real-time traffic analysis.

This module provides REST API endpoints for managing and monitoring
the real-time traffic analysis system.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from ..realtime import (
    RealTimeAnalysisPipeline, PipelineConfig, StreamProcessor,
    VideoStreamService, StreamConfig, MultiStreamManager,
    PerformanceMonitor, ViolationAnalytics, DEFAULT_PIPELINE_CONFIG, DEFAULT_STREAM_CONFIG
)


# Pydantic models for API requests/responses
class StreamStartRequest(BaseModel):
    device_id: str = Field(..., description="Unique device identifier")
    rtsp_url: str = Field(..., description="RTSP stream URL")
    config: Optional[Dict[str, Any]] = Field(None, description="Custom pipeline configuration")


class StreamStopRequest(BaseModel):
    device_id: str = Field(..., description="Device identifier to stop")


class StreamStatusResponse(BaseModel):
    device_id: str
    is_running: bool
    is_connected: bool
    frames_processed: int
    fps: float
    avg_latency_ms: float
    violations_count: int
    errors_count: int
    uptime_seconds: float


class ViolationSummary(BaseModel):
    violation_id: str
    timestamp: float
    violation_type: str
    severity: str
    device_id: str
    vehicle_id: int
    description: str


class SystemStatusResponse(BaseModel):
    system_healthy: bool
    active_streams: int
    total_streams: int
    total_violations_today: int
    avg_system_fps: float
    cpu_percent: float
    memory_percent: float
    uptime_seconds: float


# Global instances
app = FastAPI(
    title="Real-Time Traffic Analysis API",
    description="API for managing real-time traffic monitoring and violation detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
stream_processor: Optional[StreamProcessor] = None
multi_stream_manager: Optional[MultiStreamManager] = None
performance_monitor: Optional[PerformanceMonitor] = None
violation_analytics: Optional[ViolationAnalytics] = None

# WebSocket connections for real-time updates
websocket_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize the real-time analysis system."""
    global stream_processor, multi_stream_manager, performance_monitor, violation_analytics
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("api_server")
    
    try:
        # Initialize core components
        stream_processor = StreamProcessor()
        multi_stream_manager = MultiStreamManager()
        performance_monitor = PerformanceMonitor(monitoring_interval=5.0)
        violation_analytics = ViolationAnalytics(retention_days=30)
        
        # Start monitoring
        performance_monitor.start_monitoring()
        
        # Setup callbacks for real-time updates
        def on_processing_result(result):
            """Handle processing results."""
            # Record violations in analytics
            for violation in result.traffic_violations:
                violation_analytics.record_violation(
                    violation.violation_type.value,
                    result.frame_data.device_id,
                    violation.timestamp
                )
            
            # Send real-time updates to WebSocket clients
            if websocket_connections and result.traffic_violations:
                asyncio.create_task(broadcast_violations(result.traffic_violations))
        
        def on_pipeline_metrics(device_id: str, metrics):
            """Handle pipeline metrics updates."""
            performance_monitor.update_pipeline_metrics(device_id, metrics)
        
        # Add global callbacks to multi-stream manager
        multi_stream_manager.add_global_frame_callback(
            lambda device_id, frame, timestamp: None  # Frame processing handled in pipeline
        )
        
        logger.info("Real-time analysis system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown."""
    global stream_processor, multi_stream_manager, performance_monitor
    
    logger = logging.getLogger("api_server")
    
    try:
        if performance_monitor:
            performance_monitor.stop_monitoring()
        
        if multi_stream_manager:
            multi_stream_manager.stop_all_streams()
        
        logger.info("Real-time analysis system shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Stream management endpoints
@app.post("/api/streams/start", response_model=Dict[str, str])
async def start_stream(request: StreamStartRequest, background_tasks: BackgroundTasks):
    """Start processing a video stream."""
    try:
        # Create pipeline configuration
        config = DEFAULT_PIPELINE_CONFIG
        if request.config:
            # Update config with provided parameters
            for key, value in request.config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # Create stream configuration
        stream_config = DEFAULT_STREAM_CONFIG
        
        # Add stream to multi-stream manager
        success = multi_stream_manager.add_stream(
            request.device_id, 
            request.rtsp_url, 
            stream_config
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add stream")
        
        # Create and add pipeline to stream processor
        pipeline = RealTimeAnalysisPipeline(config, request.device_id)
        stream_processor.add_camera_stream(request.device_id, request.rtsp_url, config)
        
        # Start processing
        background_tasks.add_task(
            stream_processor.start_processing, request.device_id
        )
        
        # Start stream in multi-stream manager
        multi_stream_manager.start_stream(request.device_id)
        
        return {
            "status": "started",
            "device_id": request.device_id,
            "message": f"Stream processing started for device {request.device_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start stream: {str(e)}")


@app.post("/api/streams/stop", response_model=Dict[str, str])
async def stop_stream(request: StreamStopRequest):
    """Stop processing a video stream."""
    try:
        # Stop processing in stream processor
        await stream_processor.stop_processing(request.device_id)
        
        # Stop and remove from multi-stream manager
        multi_stream_manager.stop_stream(request.device_id)
        multi_stream_manager.remove_stream(request.device_id)
        
        # Remove from stream processor
        stream_processor.remove_camera_stream(request.device_id)
        
        return {
            "status": "stopped",
            "device_id": request.device_id,
            "message": f"Stream processing stopped for device {request.device_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop stream: {str(e)}")


@app.get("/api/streams/status", response_model=Dict[str, StreamStatusResponse])
async def get_streams_status():
    """Get status of all active streams."""
    try:
        status_data = stream_processor.get_all_status()
        
        response = {}
        for device_id, status in status_data.items():
            response[device_id] = StreamStatusResponse(
                device_id=device_id,
                is_running=status["is_running"],
                is_connected=True,  # Simplified for now
                frames_processed=status["metrics"]["frames_processed"],
                fps=status["metrics"]["fps"],
                avg_latency_ms=status["metrics"]["avg_latency_ms"],
                violations_count=status["metrics"]["violations_count"],
                errors_count=status["metrics"]["errors_count"],
                uptime_seconds=status["uptime_seconds"]
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stream status: {str(e)}")


@app.get("/api/streams/{device_id}/status", response_model=StreamStatusResponse)
async def get_stream_status(device_id: str):
    """Get status of a specific stream."""
    try:
        all_status = stream_processor.get_all_status()
        
        if device_id not in all_status:
            raise HTTPException(status_code=404, detail=f"Stream {device_id} not found")
        
        status = all_status[device_id]
        
        return StreamStatusResponse(
            device_id=device_id,
            is_running=status["is_running"],
            is_connected=True,
            frames_processed=status["metrics"]["frames_processed"],
            fps=status["metrics"]["fps"],
            avg_latency_ms=status["metrics"]["avg_latency_ms"],
            violations_count=status["metrics"]["violations_count"],
            errors_count=status["metrics"]["errors_count"],
            uptime_seconds=status["uptime_seconds"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stream status: {str(e)}")


# System monitoring endpoints
@app.get("/api/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get overall system status."""
    try:
        # Get aggregated metrics
        aggregated = stream_processor.get_aggregated_metrics()
        system_status = performance_monitor.get_system_status()
        
        # Calculate system health
        system_healthy = (
            aggregated["active_streams"] > 0 and
            system_status["metrics"]["system"]["cpu_percent"] < 90 and
            system_status["metrics"]["system"]["memory_percent"] < 90
        )
        
        return SystemStatusResponse(
            system_healthy=system_healthy,
            active_streams=aggregated["active_streams"],
            total_streams=aggregated["total_streams"],
            total_violations_today=aggregated["total_violations"],  # Simplified
            avg_system_fps=aggregated["average_fps"],
            cpu_percent=system_status["metrics"]["system"]["cpu_percent"],
            memory_percent=system_status["metrics"]["system"]["memory_percent"],
            uptime_seconds=system_status["monitoring"]["uptime_seconds"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@app.get("/api/system/metrics")
async def get_system_metrics():
    """Get detailed system metrics."""
    try:
        return performance_monitor.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@app.get("/api/system/alerts")
async def get_active_alerts():
    """Get active system alerts."""
    try:
        alerts = performance_monitor.get_active_alerts()
        return {
            "active_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "rule_id": alert.rule_id,
                    "timestamp": alert.timestamp,
                    "severity": alert.severity,
                    "title": alert.title,
                    "description": alert.description,
                    "metric_value": alert.metric_value,
                    "threshold": alert.threshold
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


# Violation analytics endpoints
@app.get("/api/violations/trends")
async def get_violation_trends(hours: int = 24):
    """Get violation trends for specified period."""
    try:
        trends = violation_analytics.get_violation_trends(hours)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get violation trends: {str(e)}")


@app.get("/api/violations/hotspots")
async def get_violation_hotspots():
    """Get violation hotspot analysis."""
    try:
        hotspots = violation_analytics.get_hotspot_analysis()
        return hotspots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get violation hotspots: {str(e)}")


@app.get("/api/violations/current")
async def get_current_violations():
    """Get current violation statistics."""
    try:
        stats = violation_analytics.get_current_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current violations: {str(e)}")


# WebSocket endpoint for real-time updates
@app.websocket("/api/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages if needed
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


async def broadcast_violations(violations: List):
    """Broadcast violations to all connected WebSocket clients."""
    if not websocket_connections:
        return
    
    message = {
        "type": "violations",
        "timestamp": time.time(),
        "data": [
            {
                "violation_id": violation.violation_id,
                "timestamp": violation.timestamp,
                "violation_type": violation.violation_type.value,
                "severity": violation.severity.value,
                "vehicle_id": violation.vehicle_id,
                "description": violation.description
            }
            for violation in violations
        ]
    }
    
    # Send to all connected clients
    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_json(message)
        except Exception:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for websocket in disconnected:
        websocket_connections.remove(websocket)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "stream_processor": stream_processor is not None,
            "multi_stream_manager": multi_stream_manager is not None,
            "performance_monitor": performance_monitor is not None,
            "violation_analytics": violation_analytics is not None
        }
    }


def main():
    """Main entry point for the API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-Time Traffic Analysis API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--log-level", default="info", help="Log level")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "src.realtime.api_server:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        log_level=args.log_level,
        reload=args.reload
    )


if __name__ == "__main__":
    main()