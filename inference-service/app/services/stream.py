import asyncio
import cv2
import time
import uuid
from typing import Optional, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime

from app.core import get_logger
from app.core.config import settings

logger = get_logger(__name__)


@dataclass
class StreamInfo:
    """Information about an active stream"""
    stream_id: str
    camera_id: str
    rtsp_url: str
    status: str = "stopped"  # stopped, starting, running, error
    fps: float = 0.0
    frames_processed: int = 0
    last_frame_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class StreamService:
    """Service for managing RTSP video streams"""
    
    def __init__(self, max_concurrent_streams: int = 10):
        self.max_concurrent_streams = max_concurrent_streams
        self.active_streams: Dict[str, StreamInfo] = {}
        self.stream_tasks: Dict[str, asyncio.Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_streams)
        
    async def start_stream(
        self, 
        camera_id: str, 
        rtsp_url: str,
        frame_callback: Optional[Callable] = None
    ) -> str:
        """
        Start processing an RTSP stream
        
        Args:
            camera_id: Unique identifier for the camera
            rtsp_url: RTSP URL of the camera
            frame_callback: Optional callback function to process frames
            
        Returns:
            stream_id: Unique identifier for the stream session
            
        Raises:
            ValueError: If max concurrent streams exceeded
        """
        if len(self.active_streams) >= self.max_concurrent_streams:
            raise ValueError(f"Maximum concurrent streams ({self.max_concurrent_streams}) exceeded")
        
        # Generate unique stream ID
        stream_id = str(uuid.uuid4())
        
        # Create stream info
        stream_info = StreamInfo(
            stream_id=stream_id,
            camera_id=camera_id,
            rtsp_url=rtsp_url,
            status="starting"
        )
        
        self.active_streams[stream_id] = stream_info
        
        # Start the stream processing task
        task = asyncio.create_task(
            self._process_stream(stream_info, frame_callback)
        )
        self.stream_tasks[stream_id] = task
        
        logger.info(
            "Stream started",
            stream_id=stream_id,
            camera_id=camera_id,
            rtsp_url=rtsp_url
        )
        
        return stream_id
    
    async def stop_stream(self, stream_id: str) -> bool:
        """
        Stop a running stream
        
        Args:
            stream_id: ID of the stream to stop
            
        Returns:
            bool: True if stream was stopped, False if not found
        """
        if stream_id not in self.active_streams:
            logger.warning("Attempted to stop non-existent stream", stream_id=stream_id)
            return False
        
        # Cancel the task
        if stream_id in self.stream_tasks:
            task = self.stream_tasks[stream_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.stream_tasks[stream_id]
        
        # Update status
        stream_info = self.active_streams[stream_id]
        stream_info.status = "stopped"
        
        logger.info(
            "Stream stopped",
            stream_id=stream_id,
            camera_id=stream_info.camera_id,
            frames_processed=stream_info.frames_processed
        )
        
        # Remove from active streams after a delay to allow status queries
        await asyncio.sleep(1)
        del self.active_streams[stream_id]
        
        return True
    
    def get_stream_status(self, stream_id: str) -> Optional[StreamInfo]:
        """Get status of a stream"""
        return self.active_streams.get(stream_id)
    
    def get_all_streams(self) -> Dict[str, StreamInfo]:
        """Get status of all active streams"""
        return self.active_streams.copy()
    
    async def _process_stream(
        self, 
        stream_info: StreamInfo, 
        frame_callback: Optional[Callable] = None
    ):
        """
        Process frames from an RTSP stream
        
        This method runs in a separate task and continuously reads frames
        from the RTSP stream.
        """
        cap = None
        try:
            # Open video capture in executor to avoid blocking
            cap = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._create_video_capture,
                stream_info.rtsp_url
            )
            
            if not cap or not cap.isOpened():
                raise ValueError(f"Failed to open RTSP stream: {stream_info.rtsp_url}")
            
            stream_info.status = "running"
            fps_counter = 0
            start_time = time.time()
            
            logger.info(
                "Stream processing started",
                stream_id=stream_info.stream_id,
                camera_id=stream_info.camera_id
            )
            
            while True:
                # Read frame in executor to avoid blocking
                ret, frame = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    cap.read
                )
                
                if not ret:
                    logger.warning(
                        "Failed to read frame, attempting reconnection",
                        stream_id=stream_info.stream_id
                    )
                    # Attempt to reconnect
                    cap.release()
                    await asyncio.sleep(1)
                    cap = await asyncio.get_event_loop().run_in_executor(
                        self.executor,
                        self._create_video_capture,
                        stream_info.rtsp_url
                    )
                    if not cap or not cap.isOpened():
                        raise ValueError("Failed to reconnect to RTSP stream")
                    continue
                
                # Update stream info
                stream_info.frames_processed += 1
                stream_info.last_frame_timestamp = datetime.utcnow()
                fps_counter += 1
                
                # Calculate FPS every 30 frames
                if fps_counter >= 30:
                    elapsed = time.time() - start_time
                    stream_info.fps = fps_counter / elapsed
                    fps_counter = 0
                    start_time = time.time()
                
                # Process frame with callback if provided
                if frame_callback:
                    try:
                        await frame_callback(frame, stream_info)
                    except Exception as e:
                        logger.error(
                            "Frame callback error",
                            stream_id=stream_info.stream_id,
                            error=str(e)
                        )
                
                # Add small delay to prevent CPU overload
                await asyncio.sleep(0.001)
                
        except asyncio.CancelledError:
            logger.info(
                "Stream processing cancelled",
                stream_id=stream_info.stream_id
            )
            stream_info.status = "stopped"
            raise
        except Exception as e:
            logger.error(
                "Stream processing error",
                stream_id=stream_info.stream_id,
                error=str(e)
            )
            stream_info.status = "error"
            stream_info.error_message = str(e)
        finally:
            if cap:
                cap.release()
            logger.info(
                "Stream processing ended",
                stream_id=stream_info.stream_id,
                frames_processed=stream_info.frames_processed
            )
    
    def _create_video_capture(self, rtsp_url: str) -> Optional[cv2.VideoCapture]:
        """Create OpenCV VideoCapture object (runs in thread executor)"""
        try:
            cap = cv2.VideoCapture(rtsp_url)
            # Set buffer size to reduce latency
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            # Set timeout
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10000)
            return cap
        except Exception as e:
            logger.error("Failed to create VideoCapture", rtsp_url=rtsp_url, error=str(e))
            return None
    
    async def cleanup(self):
        """Cleanup all resources"""
        # Stop all active streams
        for stream_id in list(self.active_streams.keys()):
            await self.stop_stream(stream_id)
        
        # Shutdown thread executor
        self.executor.shutdown(wait=True)


# Global instance
stream_service = StreamService(max_concurrent_streams=settings.MAX_CONCURRENT_STREAMS)


class EzvizCameraService:
    """Service specifically for EZVIZ H6C Pro 2K camera management"""
    
    def __init__(self):
        self.camera_id = "EZVIZ_H6C_PRO_2K"
        self.main_stream_url = settings.EZVIZ_RTSP_URL
        self.sub_stream_url = settings.EZVIZ_RTSP_URL_SUB
        self.camera_ip = settings.EZVIZ_IP
        self.current_stream_id: Optional[str] = None
        
    async def start_main_stream(self, frame_callback: Optional[Callable] = None) -> str:
        """Start main stream (2K resolution)"""
        logger.info("Starting EZVIZ main stream (2K)", url=self.main_stream_url)
        
        stream_id = await stream_service.start_stream(
            camera_id=self.camera_id,
            rtsp_url=self.main_stream_url,
            frame_callback=frame_callback
        )
        
        self.current_stream_id = stream_id
        return stream_id
    
    async def start_sub_stream(self, frame_callback: Optional[Callable] = None) -> str:
        """Start sub stream (720p resolution - lower latency)"""
        logger.info("Starting EZVIZ sub stream (720p)", url=self.sub_stream_url)
        
        stream_id = await stream_service.start_stream(
            camera_id=f"{self.camera_id}_SUB",
            rtsp_url=self.sub_stream_url,
            frame_callback=frame_callback
        )
        
        return stream_id
    
    async def stop_current_stream(self) -> bool:
        """Stop current active stream"""
        if self.current_stream_id:
            result = await stream_service.stop_stream(self.current_stream_id)
            if result:
                self.current_stream_id = None
            return result
        return False
    
    def get_stream_status(self) -> Optional[StreamInfo]:
        """Get status of current stream"""
        if self.current_stream_id:
            return stream_service.get_stream_status(self.current_stream_id)
        return None
    
    async def test_connectivity(self) -> Dict[str, Any]:
        """Test EZVIZ camera connectivity"""
        import socket
        
        test_result = {
            'camera_ip': self.camera_ip,
            'ping_successful': False,
            'rtsp_port_open': False,
            'http_port_open': False,
            'main_stream_accessible': False,
            'sub_stream_accessible': False,
            'test_timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Test ping (simplified socket connect)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.camera_ip, settings.EZVIZ_HTTP_PORT))
            test_result['ping_successful'] = result == 0
            sock.close()
            
            # Test RTSP port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.camera_ip, settings.EZVIZ_RTSP_PORT))
            test_result['rtsp_port_open'] = result == 0
            sock.close()
            
            # Test HTTP port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.camera_ip, settings.EZVIZ_HTTP_PORT))
            test_result['http_port_open'] = result == 0
            sock.close()
            
            # Test main stream accessibility
            cap = cv2.VideoCapture(self.main_stream_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            
            if cap.isOpened():
                ret, frame = cap.read()
                test_result['main_stream_accessible'] = ret and frame is not None
                if test_result['main_stream_accessible']:
                    test_result['main_stream_resolution'] = f"{frame.shape[1]}x{frame.shape[0]}"
            cap.release()
            
            # Test sub stream accessibility
            cap = cv2.VideoCapture(self.sub_stream_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            
            if cap.isOpened():
                ret, frame = cap.read()
                test_result['sub_stream_accessible'] = ret and frame is not None
                if test_result['sub_stream_accessible']:
                    test_result['sub_stream_resolution'] = f"{frame.shape[1]}x{frame.shape[0]}"
            cap.release()
            
        except Exception as e:
            test_result['error'] = str(e)
            logger.error("EZVIZ connectivity test failed", error=str(e))
        
        logger.info("EZVIZ connectivity test completed", **test_result)
        return test_result
    
    async def get_camera_info(self) -> Dict[str, Any]:
        """Get EZVIZ camera information"""
        return {
            'model': 'EZVIZ H6C Pro 2K',
            'camera_id': self.camera_id,
            'ip_address': self.camera_ip,
            'main_stream_url': self.main_stream_url,
            'sub_stream_url': self.sub_stream_url,
            'username': settings.EZVIZ_USERNAME,
            'rtsp_port': settings.EZVIZ_RTSP_PORT,
            'http_port': settings.EZVIZ_HTTP_PORT,
            'target_resolution': '2560x1440',
            'target_fps': 30,
            'capabilities': [
                'RTSP Streaming',
                'Night Vision',
                'Motion Detection', 
                'PTZ Control',
                'ONVIF Support'
            ]
        }


# Global EZVIZ service instance
ezviz_service = EzvizCameraService()
stream_service = StreamService()