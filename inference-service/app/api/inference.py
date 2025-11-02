from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.core import get_logger
from app.models import (
    StreamStartRequest, 
    StreamStartResponse, 
    StreamStatusResponse
)
from app.services import stream_service
from app.services.stream import ezviz_service

logger = get_logger(__name__)
router = APIRouter()


@router.post("/stream/start", response_model=StreamStartResponse)
async def start_stream(request: StreamStartRequest):
    """
    Start processing an RTSP stream from a camera
    
    This endpoint initiates video stream processing for traffic analysis.
    The stream will be processed for vehicle detection and tracking.
    """
    try:
        logger.info(
            "Stream start requested",
            camera_id=request.camera_id,
            rtsp_url=request.rtsp_url,
            zone_id=request.zone_id
        )
        
        # Validate RTSP URL format (basic check)
        if not request.rtsp_url.startswith(('rtsp://', 'http://', 'https://')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid RTSP URL format. Must start with rtsp://, http://, or https://"
            )
        
        # Start the stream
        stream_id = await stream_service.start_stream(
            camera_id=request.camera_id,
            rtsp_url=request.rtsp_url
        )
        
        logger.info(
            "Stream started successfully",
            stream_id=stream_id,
            camera_id=request.camera_id
        )
        
        return StreamStartResponse(
            success=True,
            message="Stream started successfully",
            stream_id=stream_id,
            camera_id=request.camera_id
        )
        
    except ValueError as e:
        logger.error(
            "Failed to start stream",
            camera_id=request.camera_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Unexpected error starting stream",
            camera_id=request.camera_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while starting stream"
        )


@router.post("/stream/stop/{stream_id}")
async def stop_stream(stream_id: str):
    """
    Stop processing a stream
    """
    try:
        logger.info("Stream stop requested", stream_id=stream_id)
        
        success = await stream_service.stop_stream(stream_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stream {stream_id} not found"
            )
        
        logger.info("Stream stopped successfully", stream_id=stream_id)
        
        return {"success": True, "message": "Stream stopped successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error stopping stream",
            stream_id=stream_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while stopping stream"
        )


@router.get("/stream/status/{stream_id}", response_model=StreamStatusResponse)
async def get_stream_status(stream_id: str):
    """
    Get the status of a specific stream
    """
    try:
        stream_info = stream_service.get_stream_status(stream_id)
        
        if not stream_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stream {stream_id} not found"
            )
        
        return StreamStatusResponse(
            stream_id=stream_info.stream_id,
            camera_id=stream_info.camera_id,
            status=stream_info.status,
            fps=stream_info.fps,
            frames_processed=stream_info.frames_processed,
            last_frame_timestamp=stream_info.last_frame_timestamp.isoformat() if stream_info.last_frame_timestamp else None,
            error_message=stream_info.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error getting stream status",
            stream_id=stream_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting stream status"
        )


@router.get("/streams")
async def get_all_streams():
    """
    Get status of all active streams
    """
    try:
        streams = stream_service.get_all_streams()
        
        # Convert to response format
        response = {}
        for stream_id, stream_info in streams.items():
            response[stream_id] = {
                "stream_id": stream_info.stream_id,
                "camera_id": stream_info.camera_id,
                "status": stream_info.status,
                "fps": stream_info.fps,
                "frames_processed": stream_info.frames_processed,
                "last_frame_timestamp": stream_info.last_frame_timestamp.isoformat() if stream_info.last_frame_timestamp else None,
                "error_message": stream_info.error_message,
                "created_at": stream_info.created_at.isoformat()
            }
        
        return {
            "streams": response,
            "total_streams": len(response)
        }
        
    except Exception as e:
        logger.error("Unexpected error getting all streams", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting streams"
        )


# EZVIZ H6C Pro 2K specific endpoints
@router.post("/ezviz/stream/start", response_model=StreamStartResponse)
async def start_ezviz_main_stream():
    """
    Start EZVIZ H6C Pro 2K main stream (2K resolution)
    
    This endpoint starts the main RTSP stream from the configured EZVIZ camera
    with 2560x1440 resolution for high-quality traffic analysis.
    """
    try:
        logger.info("Starting EZVIZ main stream")
        
        # Test connectivity first
        connectivity = await ezviz_service.test_connectivity()
        
        if not connectivity.get('main_stream_accessible', False):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"EZVIZ camera not accessible. Connectivity test: {connectivity}"
            )
        
        stream_id = await ezviz_service.start_main_stream()
        
        logger.info("EZVIZ main stream started", stream_id=stream_id)
        
        return StreamStartResponse(
            stream_id=stream_id,
            message="EZVIZ main stream started successfully",
            camera_id=ezviz_service.camera_id,
            rtsp_url=ezviz_service.main_stream_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start EZVIZ main stream", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start EZVIZ main stream: {str(e)}"
        )


@router.post("/ezviz/stream/start-sub", response_model=StreamStartResponse)
async def start_ezviz_sub_stream():
    """
    Start EZVIZ H6C Pro 2K sub stream (720p resolution)
    
    This endpoint starts the sub RTSP stream with lower resolution
    for testing or when lower latency is required.
    """
    try:
        logger.info("Starting EZVIZ sub stream")
        
        # Test connectivity first
        connectivity = await ezviz_service.test_connectivity()
        
        if not connectivity.get('sub_stream_accessible', False):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"EZVIZ camera sub stream not accessible. Connectivity test: {connectivity}"
            )
        
        stream_id = await ezviz_service.start_sub_stream()
        
        logger.info("EZVIZ sub stream started", stream_id=stream_id)
        
        return StreamStartResponse(
            stream_id=stream_id,
            message="EZVIZ sub stream started successfully",
            camera_id=f"{ezviz_service.camera_id}_SUB",
            rtsp_url=ezviz_service.sub_stream_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start EZVIZ sub stream", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start EZVIZ sub stream: {str(e)}"
        )


@router.post("/ezviz/stream/stop")
async def stop_ezviz_stream():
    """Stop current EZVIZ stream"""
    try:
        result = await ezviz_service.stop_current_stream()
        
        if result:
            logger.info("EZVIZ stream stopped successfully")
            return {"message": "EZVIZ stream stopped successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active EZVIZ stream found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to stop EZVIZ stream", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop EZVIZ stream: {str(e)}"
        )


@router.get("/ezviz/status")
async def get_ezviz_status():
    """Get EZVIZ camera and stream status"""
    try:
        # Get camera info
        camera_info = await ezviz_service.get_camera_info()
        
        # Get current stream status
        stream_status = ezviz_service.get_stream_status()
        
        # Get connectivity status
        connectivity = await ezviz_service.test_connectivity()
        
        return {
            "camera_info": camera_info,
            "stream_status": {
                "stream_id": stream_status.stream_id if stream_status else None,
                "status": stream_status.status if stream_status else "no_stream",
                "fps": stream_status.fps if stream_status else 0,
                "frames_processed": stream_status.frames_processed if stream_status else 0,
                "last_frame_timestamp": stream_status.last_frame_timestamp.isoformat() if stream_status and stream_status.last_frame_timestamp else None,
                "error_message": stream_status.error_message if stream_status else None
            },
            "connectivity": connectivity
        }
        
    except Exception as e:
        logger.error("Failed to get EZVIZ status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get EZVIZ status: {str(e)}"
        )


@router.get("/ezviz/test-connectivity")
async def test_ezviz_connectivity():
    """Test EZVIZ camera connectivity"""
    try:
        connectivity = await ezviz_service.test_connectivity()
        
        # Determine overall status
        overall_status = "healthy"
        if not connectivity.get('ping_successful', False):
            overall_status = "unreachable"
        elif not connectivity.get('rtsp_port_open', False):
            overall_status = "rtsp_unavailable"
        elif not connectivity.get('main_stream_accessible', False):
            overall_status = "stream_unavailable"
        
        return {
            "overall_status": overall_status,
            "details": connectivity,
            "recommendations": _get_connectivity_recommendations(connectivity)
        }
        
    except Exception as e:
        logger.error("Failed to test EZVIZ connectivity", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test EZVIZ connectivity: {str(e)}"
        )


def _get_connectivity_recommendations(connectivity: Dict[str, Any]) -> list:
    """Generate recommendations based on connectivity test results"""
    recommendations = []
    
    if not connectivity.get('ping_successful', False):
        recommendations.append("Check if EZVIZ camera is powered on and connected to network")
        recommendations.append("Verify IP address configuration (expected: 192.168.1.100)")
        recommendations.append("Check network connectivity between inference service and camera")
    
    if not connectivity.get('rtsp_port_open', False):
        recommendations.append("Enable RTSP in EZVIZ app settings")
        recommendations.append("Check firewall settings on camera")
        recommendations.append("Verify RTSP port 554 is not blocked")
    
    if not connectivity.get('main_stream_accessible', False):
        recommendations.append("Check RTSP credentials (username: admin)")
        recommendations.append("Verify RTSP URL format and authentication")
        recommendations.append("Try sub stream if main stream fails")
    
    if len(recommendations) == 0:
        recommendations.append("All connectivity tests passed - camera is ready for use")
    
    return recommendations