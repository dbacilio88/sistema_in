"""
WebSocket endpoint para streaming de video desde cámaras con detección en tiempo real
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Optional
import json
import base64
import numpy as np
import cv2
import asyncio
from datetime import datetime

from app.core import get_logger
from app.services.model_service import model_service
from app.api.websocket import detector

logger = get_logger(__name__)
router = APIRouter()


class CameraStreamManager:
    """
    Manages camera streams and performs real-time detection
    """
    def __init__(self):
        self.active_streams: Dict[str, dict] = {}
        
    async def start_stream(
        self, 
        device_id: str, 
        camera_url: str,
        websocket: WebSocket,
        config: Dict
    ):
        """
        Start streaming from camera with real-time detection
        
        Args:
            device_id: Unique device identifier
            camera_url: RTSP or HTTP URL of camera
            websocket: WebSocket connection to send frames
            config: Detection configuration
        """
        logger.info(f"Starting camera stream for device {device_id} from {camera_url}")
        
        # Initialize detector models if needed
        if not model_service._initialized:
            await detector.initialize_models()
        
        # Open video capture
        cap = cv2.VideoCapture(camera_url)
        
        if not cap.isOpened():
            logger.error(f"Failed to open camera stream: {camera_url}")
            await websocket.send_json({
                "type": "error",
                "error": "No se pudo conectar con la cámara"
            })
            return
        
        # Store stream info
        self.active_streams[device_id] = {
            "capture": cap,
            "websocket": websocket,
            "config": config,
            "active": True
        }
        
        frame_count = 0
        
        try:
            while self.active_streams.get(device_id, {}).get("active", False):
                # Read frame
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame from device {device_id}")
                    # Try to reconnect
                    cap.release()
                    await asyncio.sleep(1)
                    cap = cv2.VideoCapture(camera_url)
                    continue
                
                frame_count += 1
                
                # Process every Nth frame for performance (default: process all frames)
                process_interval = config.get('process_interval', 1)
                if frame_count % process_interval != 0:
                    continue
                
                # Encode frame to base64
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Perform detection
                result = await detector.process_frame(frame_base64, config)
                
                # Send frame with detections to client
                if "error" not in result:
                    await websocket.send_json({
                        "type": "frame",
                        "frame": frame_base64,
                        "detections": result.get("detections", []),
                        "frame_number": frame_count,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Small delay to control framerate
                await asyncio.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            logger.error(f"Error in camera stream {device_id}: {str(e)}", exc_info=True)
        finally:
            # Cleanup
            cap.release()
            if device_id in self.active_streams:
                del self.active_streams[device_id]
            logger.info(f"Camera stream stopped for device {device_id}")
    
    def stop_stream(self, device_id: str):
        """Stop a camera stream"""
        if device_id in self.active_streams:
            self.active_streams[device_id]["active"] = False
            logger.info(f"Stopping stream for device {device_id}")


# Global stream manager
stream_manager = CameraStreamManager()


@router.websocket("/ws/camera/{device_id}")
async def websocket_camera_stream(
    websocket: WebSocket,
    device_id: str,
    camera_url: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for camera streaming with detection
    
    Client connects and receives frames with detection results
    
    Query params:
        camera_url: Camera RTSP/HTTP URL (if not provided, fetches from Django)
    """
    await websocket.accept()
    logger.info(f"Camera stream WebSocket connected for device {device_id}")
    
    try:
        # Get camera URL from Django if not provided
        if not camera_url:
            # TODO: Fetch from Django API
            # For now, construct from device_id
            camera_url = f"rtsp://admin:admin@camera-{device_id}/stream"
        
        # Wait for configuration from client (optional)
        config = {
            'confidence_threshold': 0.7,
            'enable_ocr': True,
            'enable_speed': True,
            'infractions': ['speeding', 'red_light', 'lane_invasion'],
            'speed_limit': 60,
            'process_interval': 1  # Process every frame
        }
        
        # Check if client sends initial config
        try:
            data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            message = json.loads(data)
            if message.get('type') == 'config':
                config.update(message.get('config', {}))
                logger.info(f"Received config from client: {config}")
        except asyncio.TimeoutError:
            logger.info("No initial config from client, using defaults")
        
        # Start streaming
        await stream_manager.start_stream(
            device_id=device_id,
            camera_url=camera_url,
            websocket=websocket,
            config=config
        )
        
    except WebSocketDisconnect:
        stream_manager.stop_stream(device_id)
        logger.info(f"Client disconnected from camera stream {device_id}")
    except Exception as e:
        logger.error(f"WebSocket camera stream error: {str(e)}", exc_info=True)
        stream_manager.stop_stream(device_id)
        try:
            await websocket.close()
        except:
            pass
