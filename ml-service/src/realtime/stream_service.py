"""
Stream service for handling video streams (RTSP, file, webcam).

Provides robust video stream handling with reconnection and buffering capabilities.
"""

import cv2
import time
import threading
import logging
from typing import Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from collections import deque
import numpy as np
from urllib.parse import urlparse


@dataclass
class StreamConfig:
    """Configuration for video stream handling."""
    
    # Connection settings
    reconnect_attempts: int = 5
    reconnect_delay_seconds: float = 2.0
    connection_timeout_seconds: float = 10.0
    
    # Buffer settings
    buffer_size: int = 10  # Number of frames to buffer
    drop_frames_on_delay: bool = True  # Drop frames if processing is slow
    
    # Stream settings  
    rtsp_transport: str = "tcp"  # "tcp" or "udp"
    opencv_backend: int = cv2.CAP_FFMPEG
    
    # Quality settings
    target_fps: Optional[float] = None  # Limit FPS (None = no limit)
    resize_width: Optional[int] = None  # Resize frame width (None = no resize)
    resize_height: Optional[int] = None  # Resize frame height (None = no resize)


@dataclass 
class StreamStats:
    """Statistics for stream performance monitoring."""
    
    frames_read: int = 0
    frames_dropped: int = 0
    reconnections: int = 0
    total_errors: int = 0
    
    # Timing statistics
    avg_read_time_ms: float = 0.0
    fps: float = 0.0
    
    # Connection info
    is_connected: bool = False
    last_frame_time: Optional[float] = None
    connection_start_time: Optional[float] = None
    
    # Error tracking
    last_error: Optional[str] = None
    error_count_recent: int = 0


class VideoStreamService:
    """
    Robust video stream service supporting RTSP, file, and webcam sources.
    
    Features:
    - Automatic reconnection on connection loss
    - Frame buffering and dropping for real-time processing
    - Performance monitoring and statistics
    - Thread-safe operation
    - Multiple source types (RTSP, file, webcam)
    """
    
    def __init__(self, source: str, config: StreamConfig = None):
        """
        Initialize video stream service.
        
        Args:
            source: Video source (RTSP URL, file path, or webcam index)
            config: Stream configuration
        """
        self.source = source
        self.config = config or StreamConfig()
        self.logger = logging.getLogger(f"stream.{self._get_source_id()}")
        
        # OpenCV VideoCapture
        self.capture: Optional[cv2.VideoCapture] = None
        
        # Threading for continuous reading
        self.reading_thread: Optional[threading.Thread] = None
        self.is_running = False
        self._lock = threading.Lock()
        
        # Frame buffer
        self.frame_buffer = deque(maxlen=self.config.buffer_size)
        self.current_frame: Optional[np.ndarray] = None
        self.current_timestamp: Optional[float] = None
        
        # Statistics and monitoring
        self.stats = StreamStats()
        self.last_fps_calc = time.time()
        self.fps_frame_count = 0
        
        # Callbacks for events
        self.frame_callbacks: list = []
        self.error_callbacks: list = []
        self.connection_callbacks: list = []
    
    def _get_source_id(self) -> str:
        """Get a short identifier for the source."""
        if isinstance(self.source, str):
            if self.source.startswith(('rtsp://', 'http://', 'https://')):
                parsed = urlparse(self.source)
                return f"{parsed.hostname}:{parsed.port or 554}"
            elif self.source.isdigit():
                return f"webcam_{self.source}"
            else:
                return f"file_{self.source.split('/')[-1]}"
        else:
            return f"webcam_{self.source}"
    
    def add_frame_callback(self, callback: Callable[[np.ndarray, float], None]):
        """Add callback for new frames."""
        self.frame_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable[[str], None]):
        """Add callback for errors.""" 
        self.error_callbacks.append(callback)
    
    def add_connection_callback(self, callback: Callable[[bool], None]):
        """Add callback for connection status changes."""
        self.connection_callbacks.append(callback)
    
    def start(self) -> bool:
        """
        Start the video stream.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.is_running:
            self.logger.warning("Stream already running")
            return True
        
        if not self._connect():
            return False
        
        self.is_running = True
        self.reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
        self.reading_thread.start()
        
        self.logger.info("Video stream started")
        return True
    
    def stop(self):
        """Stop the video stream."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.reading_thread:
            self.reading_thread.join(timeout=5.0)
        
        self._disconnect()
        self.logger.info("Video stream stopped")
    
    def _connect(self) -> bool:
        """Establish connection to video source."""
        self.logger.info(f"Connecting to video source: {self.source}")
        
        try:
            # Create VideoCapture object
            if isinstance(self.source, str) and self.source.isdigit():
                # Webcam index
                self.capture = cv2.VideoCapture(int(self.source), self.config.opencv_backend)
            else:
                # File or RTSP URL
                self.capture = cv2.VideoCapture(self.source, self.config.opencv_backend)
            
            if not self.capture.isOpened():
                raise RuntimeError("Failed to open video source")
            
            # Configure capture properties
            self._configure_capture()
            
            # Test reading a frame
            ret, frame = self.capture.read()
            if not ret or frame is None:
                raise RuntimeError("Failed to read initial frame")
            
            # Update statistics
            self.stats.is_connected = True
            self.stats.connection_start_time = time.time()
            
            # Notify connection callbacks
            for callback in self.connection_callbacks:
                try:
                    callback(True)
                except Exception as e:
                    self.logger.error(f"Connection callback error: {e}")
            
            self.logger.info("Video connection established")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.stats.last_error = str(e)
            self.stats.total_errors += 1
            self._disconnect()
            return False
    
    def _disconnect(self):
        """Disconnect from video source."""
        if self.capture:
            self.capture.release()
            self.capture = None
        
        self.stats.is_connected = False
        
        # Notify connection callbacks
        for callback in self.connection_callbacks:
            try:
                callback(False)
            except Exception as e:
                self.logger.error(f"Connection callback error: {e}")
    
    def _configure_capture(self):
        """Configure OpenCV VideoCapture properties."""
        if not self.capture:
            return
        
        try:
            # Buffer size (reduce for real-time streaming)
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # FPS setting (if specified)
            if self.config.target_fps:
                self.capture.set(cv2.CAP_PROP_FPS, self.config.target_fps)
            
            # Frame size (if specified)
            if self.config.resize_width:
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resize_width)
            if self.config.resize_height:
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resize_height)
            
            # RTSP-specific settings
            if isinstance(self.source, str) and self.source.startswith('rtsp://'):
                # TCP transport for more reliable streaming
                if self.config.rtsp_transport.lower() == "tcp":
                    self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
                
            self.logger.debug("Capture properties configured")
            
        except Exception as e:
            self.logger.warning(f"Error configuring capture properties: {e}")
    
    def _reading_loop(self):
        """Main reading loop running in separate thread."""
        consecutive_errors = 0
        last_frame_time = time.time()
        
        while self.is_running:
            try:
                if not self.stats.is_connected:
                    # Attempt reconnection
                    if self._connect():
                        consecutive_errors = 0
                    else:
                        consecutive_errors += 1
                        time.sleep(self.config.reconnect_delay_seconds * min(consecutive_errors, 5))
                        continue
                
                # Read frame
                read_start = time.perf_counter()
                ret, frame = self.capture.read()
                read_time = (time.perf_counter() - read_start) * 1000
                
                if not ret or frame is None:
                    self.logger.warning("Failed to read frame")
                    self._handle_read_error()
                    consecutive_errors += 1
                    continue
                
                # Update read timing statistics
                if self.stats.avg_read_time_ms == 0:
                    self.stats.avg_read_time_ms = read_time
                else:
                    # Exponential moving average
                    self.stats.avg_read_time_ms = 0.9 * self.stats.avg_read_time_ms + 0.1 * read_time
                
                # Apply frame processing
                processed_frame = self._process_frame(frame)
                current_time = time.time()
                
                # Update buffer and current frame
                with self._lock:
                    if self.config.drop_frames_on_delay and len(self.frame_buffer) >= self.config.buffer_size:
                        # Drop oldest frame if buffer is full
                        dropped_frame = self.frame_buffer.popleft()
                        self.stats.frames_dropped += 1
                    
                    self.frame_buffer.append((processed_frame, current_time))
                    self.current_frame = processed_frame
                    self.current_timestamp = current_time
                    self.stats.last_frame_time = current_time
                
                # Update statistics
                self.stats.frames_read += 1
                consecutive_errors = 0
                
                # Calculate FPS
                self._update_fps()
                
                # Call frame callbacks
                for callback in self.frame_callbacks:
                    try:
                        callback(processed_frame, current_time)
                    except Exception as e:
                        self.logger.error(f"Frame callback error: {e}")
                
                # Frame rate limiting
                if self.config.target_fps:
                    target_interval = 1.0 / self.config.target_fps
                    elapsed = current_time - last_frame_time
                    sleep_time = target_interval - elapsed
                    
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                
                last_frame_time = current_time
                
            except Exception as e:
                self.logger.error(f"Reading loop error: {e}")
                consecutive_errors += 1
                self.stats.total_errors += 1
                self.stats.last_error = str(e)
                
                # Call error callbacks
                for callback in self.error_callbacks:
                    try:
                        callback(str(e))
                    except Exception as callback_error:
                        self.logger.error(f"Error callback error: {callback_error}")
                
                # Backoff on consecutive errors
                time.sleep(min(consecutive_errors * 0.5, 5.0))
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process frame (resize, format conversion, etc.)."""
        processed = frame.copy()
        
        # Resize if configured
        if (self.config.resize_width and self.config.resize_height and 
            (frame.shape[1] != self.config.resize_width or frame.shape[0] != self.config.resize_height)):
            processed = cv2.resize(processed, (self.config.resize_width, self.config.resize_height))
        
        return processed
    
    def _handle_read_error(self):
        """Handle frame read errors."""
        self.stats.error_count_recent += 1
        
        # If too many recent errors, trigger reconnection
        if self.stats.error_count_recent >= 10:
            self.logger.warning("Too many read errors, triggering reconnection")
            self._disconnect()
            self.stats.reconnections += 1
            self.stats.error_count_recent = 0
    
    def _update_fps(self):
        """Update FPS calculation."""
        self.fps_frame_count += 1
        current_time = time.time()
        
        # Calculate FPS every second
        if current_time - self.last_fps_calc >= 1.0:
            self.stats.fps = self.fps_frame_count / (current_time - self.last_fps_calc)
            self.fps_frame_count = 0
            self.last_fps_calc = current_time
    
    def get_frame(self) -> Tuple[Optional[np.ndarray], Optional[float]]:
        """
        Get the most recent frame.
        
        Returns:
            Tuple of (frame, timestamp) or (None, None) if no frame available
        """
        with self._lock:
            return self.current_frame, self.current_timestamp
    
    def get_latest_frames(self, count: int = 1) -> list:
        """
        Get the latest N frames from buffer.
        
        Args:
            count: Number of frames to retrieve
            
        Returns:
            List of (frame, timestamp) tuples
        """
        with self._lock:
            frames = list(self.frame_buffer)
            return frames[-count:] if frames else []
    
    def get_statistics(self) -> StreamStats:
        """Get current stream statistics."""
        return self.stats
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive stream status."""
        return {
            "source": self.source,
            "is_running": self.is_running,
            "is_connected": self.stats.is_connected,
            "frames_read": self.stats.frames_read,
            "frames_dropped": self.stats.frames_dropped,
            "fps": self.stats.fps,
            "avg_read_time_ms": self.stats.avg_read_time_ms,
            "reconnections": self.stats.reconnections,
            "total_errors": self.stats.total_errors,
            "last_error": self.stats.last_error,
            "buffer_size": len(self.frame_buffer),
            "uptime_seconds": time.time() - self.stats.connection_start_time if self.stats.connection_start_time else 0
        }
    
    def is_healthy(self) -> bool:
        """Check if stream is healthy (connected and receiving frames)."""
        if not self.stats.is_connected or not self.is_running:
            return False
        
        # Check if we've received frames recently (within 5 seconds)
        if self.stats.last_frame_time:
            time_since_last_frame = time.time() - self.stats.last_frame_time
            return time_since_last_frame < 5.0
        
        return False
    
    def restart(self) -> bool:
        """Restart the stream connection."""
        self.logger.info("Restarting stream connection")
        
        was_running = self.is_running
        if was_running:
            self.stop()
        
        # Reset error count
        self.stats.error_count_recent = 0
        
        if was_running:
            return self.start()
        
        return True


class MultiStreamManager:
    """
    Manager for multiple video streams.
    
    Handles multiple camera streams with centralized monitoring and control.
    """
    
    def __init__(self):
        """Initialize multi-stream manager."""
        self.logger = logging.getLogger("multi_stream_manager")
        self.streams: Dict[str, VideoStreamService] = {}
        self.stream_configs: Dict[str, StreamConfig] = {}
        
        # Global callbacks
        self.global_frame_callbacks: list = []
        self.global_error_callbacks: list = []
        self.global_connection_callbacks: list = []
    
    def add_stream(self, stream_id: str, source: str, config: StreamConfig = None) -> bool:
        """
        Add a new video stream.
        
        Args:
            stream_id: Unique identifier for the stream
            source: Video source (RTSP URL, file path, or webcam index)
            config: Stream configuration
            
        Returns:
            bool: True if added successfully
        """
        if stream_id in self.streams:
            self.logger.error(f"Stream {stream_id} already exists")
            return False
        
        try:
            stream_config = config or StreamConfig()
            stream = VideoStreamService(source, stream_config)
            
            # Add global callbacks
            for callback in self.global_frame_callbacks:
                stream.add_frame_callback(lambda frame, ts, sid=stream_id: callback(sid, frame, ts))
            
            for callback in self.global_error_callbacks:
                stream.add_error_callback(lambda error, sid=stream_id: callback(sid, error))
            
            for callback in self.global_connection_callbacks:
                stream.add_connection_callback(lambda connected, sid=stream_id: callback(sid, connected))
            
            self.streams[stream_id] = stream
            self.stream_configs[stream_id] = stream_config
            
            self.logger.info(f"Added stream {stream_id}: {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add stream {stream_id}: {e}")
            return False
    
    def remove_stream(self, stream_id: str) -> bool:
        """Remove a video stream."""
        if stream_id not in self.streams:
            self.logger.error(f"Stream {stream_id} not found")
            return False
        
        try:
            self.streams[stream_id].stop()
            del self.streams[stream_id]
            del self.stream_configs[stream_id]
            
            self.logger.info(f"Removed stream {stream_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove stream {stream_id}: {e}")
            return False
    
    def start_stream(self, stream_id: str) -> bool:
        """Start a specific stream."""
        if stream_id not in self.streams:
            self.logger.error(f"Stream {stream_id} not found")
            return False
        
        return self.streams[stream_id].start()
    
    def stop_stream(self, stream_id: str) -> bool:
        """Stop a specific stream."""
        if stream_id not in self.streams:
            self.logger.error(f"Stream {stream_id} not found")
            return False
        
        self.streams[stream_id].stop()
        return True
    
    def start_all_streams(self) -> Dict[str, bool]:
        """Start all streams."""
        results = {}
        for stream_id in self.streams:
            results[stream_id] = self.start_stream(stream_id)
        return results
    
    def stop_all_streams(self):
        """Stop all streams."""
        for stream in self.streams.values():
            stream.stop()
    
    def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific stream."""
        if stream_id not in self.streams:
            return None
        return self.streams[stream_id].get_status()
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all streams."""
        return {
            stream_id: stream.get_status()
            for stream_id, stream in self.streams.items()
        }
    
    def get_healthy_streams(self) -> list:
        """Get list of healthy stream IDs."""
        return [
            stream_id for stream_id, stream in self.streams.items()
            if stream.is_healthy()
        ]
    
    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics across all streams."""
        total_frames = sum(stream.stats.frames_read for stream in self.streams.values())
        total_dropped = sum(stream.stats.frames_dropped for stream in self.streams.values())
        total_errors = sum(stream.stats.total_errors for stream in self.streams.values())
        total_reconnections = sum(stream.stats.reconnections for stream in self.streams.values())
        
        healthy_streams = len(self.get_healthy_streams())
        avg_fps = sum(stream.stats.fps for stream in self.streams.values()) / len(self.streams) if self.streams else 0
        
        return {
            "total_streams": len(self.streams),
            "healthy_streams": healthy_streams,
            "total_frames_read": total_frames,
            "total_frames_dropped": total_dropped,
            "total_errors": total_errors,
            "total_reconnections": total_reconnections,
            "average_fps": avg_fps,
            "drop_rate": total_dropped / total_frames if total_frames > 0 else 0
        }
    
    def add_global_frame_callback(self, callback: Callable[[str, np.ndarray, float], None]):
        """Add global frame callback for all streams."""
        self.global_frame_callbacks.append(callback)
        
        # Add to existing streams
        for stream_id, stream in self.streams.items():
            stream.add_frame_callback(lambda frame, ts, sid=stream_id: callback(sid, frame, ts))
    
    def add_global_error_callback(self, callback: Callable[[str, str], None]):
        """Add global error callback for all streams."""
        self.global_error_callbacks.append(callback)
        
        # Add to existing streams
        for stream_id, stream in self.streams.items():
            stream.add_error_callback(lambda error, sid=stream_id: callback(sid, error))
    
    def add_global_connection_callback(self, callback: Callable[[str, bool], None]):
        """Add global connection callback for all streams."""
        self.global_connection_callbacks.append(callback)
        
        # Add to existing streams
        for stream_id, stream in self.streams.items():
            stream.add_connection_callback(lambda connected, sid=stream_id: callback(sid, connected))