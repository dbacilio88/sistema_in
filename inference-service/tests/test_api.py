import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Traffic Inference Service"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    @patch('app.services.health.health_service.get_health_status')
    def test_health_endpoint_healthy(self, mock_health_status, client):
        """Test health endpoint when all services are healthy"""
        from app.models import ServiceStatus, ServiceHealth
        
        # Mock healthy responses
        mock_health_status.return_value = asyncio.coroutine(lambda: {
            "database": ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=10.5,
                details={"connection": "ok"}
            ),
            "redis": ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=5.2,
                details={"connection": "ok"}
            ),
            "storage": ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=15.8,
                details={"connection": "ok", "note": "simplified_check"}
            )
        })()
        
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "services" in data
        assert "uptime_seconds" in data
        assert len(data["services"]) == 3
    
    @patch('app.services.health.health_service.get_health_status')
    def test_health_endpoint_unhealthy(self, mock_health_status, client):
        """Test health endpoint when some services are unhealthy"""
        from app.models import ServiceStatus, ServiceHealth
        
        # Mock unhealthy responses
        mock_health_status.return_value = asyncio.coroutine(lambda: {
            "database": ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=1000.0,
                details={"error": "Connection timeout", "connection": "failed"}
            ),
            "redis": ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=5.2,
                details={"connection": "ok"}
            ),
            "storage": ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=15.8,
                details={"connection": "ok", "note": "simplified_check"}
            )
        })()
        
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["services"]["database"]["status"] == "unhealthy"


class TestInferenceEndpoints:
    """Test inference/stream endpoints"""
    
    @patch('app.services.stream.stream_service.start_stream')
    def test_start_stream_success(self, mock_start_stream, client):
        """Test successful stream start"""
        mock_start_stream.return_value = asyncio.coroutine(lambda: "test-stream-id-123")()
        
        payload = {
            "camera_id": "CAM001",
            "rtsp_url": "rtsp://test.example.com:554/stream",
            "zone_id": "ZONE001",
            "enable_detection": True,
            "enable_tracking": True
        }
        
        response = client.post("/api/inference/stream/start", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["stream_id"] == "test-stream-id-123"
        assert data["camera_id"] == "CAM001"
        assert "message" in data
    
    def test_start_stream_invalid_url(self, client):
        """Test stream start with invalid RTSP URL"""
        payload = {
            "camera_id": "CAM001",
            "rtsp_url": "invalid://not-rtsp-url",
            "enable_detection": True,
            "enable_tracking": True
        }
        
        response = client.post("/api/inference/stream/start", json=payload)
        assert response.status_code == 400
        assert "Invalid RTSP URL format" in response.json()["detail"]
    
    @patch('app.services.stream.stream_service.start_stream')
    def test_start_stream_max_concurrent_exceeded(self, mock_start_stream, client):
        """Test stream start when max concurrent streams exceeded"""
        mock_start_stream.side_effect = ValueError("Maximum concurrent streams (10) exceeded")
        
        payload = {
            "camera_id": "CAM001",
            "rtsp_url": "rtsp://test.example.com:554/stream",
            "enable_detection": True,
            "enable_tracking": True
        }
        
        response = client.post("/api/inference/stream/start", json=payload)
        assert response.status_code == 400
        assert "Maximum concurrent streams" in response.json()["detail"]
    
    @patch('app.services.stream.stream_service.stop_stream')
    def test_stop_stream_success(self, mock_stop_stream, client):
        """Test successful stream stop"""
        mock_stop_stream.return_value = asyncio.coroutine(lambda: True)()
        
        response = client.post("/api/inference/stream/stop/test-stream-id")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    @patch('app.services.stream.stream_service.stop_stream')
    def test_stop_stream_not_found(self, mock_stop_stream, client):
        """Test stop stream when stream not found"""
        mock_stop_stream.return_value = asyncio.coroutine(lambda: False)()
        
        response = client.post("/api/inference/stream/stop/non-existent-stream")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch('app.services.stream.stream_service.get_stream_status')
    def test_get_stream_status_success(self, mock_get_status, client):
        """Test successful stream status retrieval"""
        from app.services.stream import StreamInfo
        from datetime import datetime
        
        mock_stream_info = StreamInfo(
            stream_id="test-stream-id",
            camera_id="CAM001",
            rtsp_url="rtsp://test.example.com:554/stream",
            status="running",
            fps=30.0,
            frames_processed=1500,
            last_frame_timestamp=datetime.utcnow()
        )
        mock_get_status.return_value = mock_stream_info
        
        response = client.get("/api/inference/stream/status/test-stream-id")
        assert response.status_code == 200
        
        data = response.json()
        assert data["stream_id"] == "test-stream-id"
        assert data["camera_id"] == "CAM001"
        assert data["status"] == "running"
        assert data["fps"] == 30.0
        assert data["frames_processed"] == 1500
    
    @patch('app.services.stream.stream_service.get_stream_status')
    def test_get_stream_status_not_found(self, mock_get_status, client):
        """Test get stream status when stream not found"""
        mock_get_status.return_value = None
        
        response = client.get("/api/inference/stream/status/non-existent-stream")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch('app.services.stream.stream_service.get_all_streams')
    def test_get_all_streams(self, mock_get_all_streams, client):
        """Test get all streams endpoint"""
        from app.services.stream import StreamInfo
        from datetime import datetime
        
        mock_streams = {
            "stream-1": StreamInfo(
                stream_id="stream-1",
                camera_id="CAM001",
                rtsp_url="rtsp://test1.example.com:554/stream",
                status="running",
                fps=30.0,
                frames_processed=1500
            ),
            "stream-2": StreamInfo(
                stream_id="stream-2",
                camera_id="CAM002",
                rtsp_url="rtsp://test2.example.com:554/stream",
                status="error",
                fps=0.0,
                frames_processed=100,
                error_message="Connection lost"
            )
        }
        mock_get_all_streams.return_value = mock_streams
        
        response = client.get("/api/inference/streams")
        assert response.status_code == 200
        
        data = response.json()
        assert "streams" in data
        assert "total_streams" in data
        assert data["total_streams"] == 2
        assert len(data["streams"]) == 2