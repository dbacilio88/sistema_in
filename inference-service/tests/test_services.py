import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.stream import StreamService, StreamInfo
from app.services.health import HealthService
from app.models import ServiceStatus, ServiceHealth


class TestStreamService:
    """Test StreamService functionality"""
    
    @pytest.fixture
    def stream_service(self):
        """Create a StreamService instance for testing"""
        return StreamService(max_concurrent_streams=2)
    
    @pytest.mark.asyncio
    async def test_start_stream_success(self, stream_service):
        """Test successful stream start"""
        with patch.object(stream_service, '_process_stream') as mock_process:
            mock_process.return_value = AsyncMock()
            
            stream_id = await stream_service.start_stream(
                camera_id="CAM001",
                rtsp_url="rtsp://test.example.com:554/stream"
            )
            
            assert stream_id is not None
            assert len(stream_id) > 0
            assert stream_id in stream_service.active_streams
            
            stream_info = stream_service.active_streams[stream_id]
            assert stream_info.camera_id == "CAM001"
            assert stream_info.rtsp_url == "rtsp://test.example.com:554/stream"
            assert stream_info.status == "starting"
    
    @pytest.mark.asyncio
    async def test_start_stream_max_concurrent_exceeded(self, stream_service):
        """Test stream start when max concurrent limit is exceeded"""
        # Fill up to max capacity
        with patch.object(stream_service, '_process_stream') as mock_process:
            mock_process.return_value = AsyncMock()
            
            # Start max allowed streams
            for i in range(2):
                await stream_service.start_stream(
                    camera_id=f"CAM{i:03d}",
                    rtsp_url=f"rtsp://test{i}.example.com:554/stream"
                )
            
            # Try to start one more - should fail
            with pytest.raises(ValueError, match="Maximum concurrent streams"):
                await stream_service.start_stream(
                    camera_id="CAM999",
                    rtsp_url="rtsp://overflow.example.com:554/stream"
                )
    
    @pytest.mark.asyncio
    async def test_stop_stream_success(self, stream_service):
        """Test successful stream stop"""
        with patch.object(stream_service, '_process_stream') as mock_process:
            mock_process.return_value = AsyncMock()
            
            # Start a stream
            stream_id = await stream_service.start_stream(
                camera_id="CAM001",
                rtsp_url="rtsp://test.example.com:554/stream"
            )
            
            # Stop the stream
            result = await stream_service.stop_stream(stream_id)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_stop_stream_not_found(self, stream_service):
        """Test stop stream when stream doesn't exist"""
        result = await stream_service.stop_stream("non-existent-stream-id")
        assert result is False
    
    def test_get_stream_status(self, stream_service):
        """Test get stream status"""
        # Create a mock stream info
        stream_info = StreamInfo(
            stream_id="test-stream",
            camera_id="CAM001",
            rtsp_url="rtsp://test.example.com:554/stream",
            status="running"
        )
        stream_service.active_streams["test-stream"] = stream_info
        
        # Get status
        result = stream_service.get_stream_status("test-stream")
        assert result is not None
        assert result.stream_id == "test-stream"
        assert result.camera_id == "CAM001"
        assert result.status == "running"
        
        # Test non-existent stream
        result = stream_service.get_stream_status("non-existent")
        assert result is None
    
    def test_get_all_streams(self, stream_service):
        """Test get all streams"""
        # Add some mock streams
        for i in range(3):
            stream_info = StreamInfo(
                stream_id=f"stream-{i}",
                camera_id=f"CAM{i:03d}",
                rtsp_url=f"rtsp://test{i}.example.com:554/stream",
                status="running"
            )
            stream_service.active_streams[f"stream-{i}"] = stream_info
        
        result = stream_service.get_all_streams()
        assert len(result) == 3
        assert "stream-0" in result
        assert "stream-1" in result
        assert "stream-2" in result


class TestHealthService:
    """Test HealthService functionality"""
    
    @pytest.fixture
    def health_service(self):
        """Create a HealthService instance for testing"""
        return HealthService()
    
    @pytest.mark.asyncio
    async def test_check_database_success(self, health_service):
        """Test successful database health check"""
        with patch('asyncpg.connect') as mock_connect:
            mock_conn = AsyncMock()
            mock_connect.return_value = mock_conn
            mock_conn.execute.return_value = None
            mock_conn.close.return_value = None
            
            result = await health_service.check_database()
            
            assert result.status == ServiceStatus.HEALTHY
            assert result.response_time_ms > 0
            assert result.details["connection"] == "ok"
    
    @pytest.mark.asyncio
    async def test_check_database_failure(self, health_service):
        """Test database health check failure"""
        with patch('asyncpg.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            result = await health_service.check_database()
            
            assert result.status == ServiceStatus.UNHEALTHY
            assert result.response_time_ms > 0
            assert "Connection failed" in result.details["error"]
    
    @pytest.mark.asyncio
    async def test_check_redis_success(self, health_service):
        """Test successful Redis health check"""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True
            mock_client.close.return_value = None
            
            result = await health_service.check_redis()
            
            assert result.status == ServiceStatus.HEALTHY
            assert result.response_time_ms > 0
            assert result.details["connection"] == "ok"
    
    @pytest.mark.asyncio
    async def test_check_redis_failure(self, health_service):
        """Test Redis health check failure"""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis.side_effect = Exception("Redis connection failed")
            
            result = await health_service.check_redis()
            
            assert result.status == ServiceStatus.UNHEALTHY
            assert result.response_time_ms > 0
            assert "Redis connection failed" in result.details["error"]
    
    @pytest.mark.asyncio
    async def test_check_storage_success(self, health_service):
        """Test successful storage health check"""
        result = await health_service.check_storage()
        
        # For now this is a simplified check that always returns healthy
        assert result.status == ServiceStatus.HEALTHY
        assert result.response_time_ms > 0
        assert result.details["connection"] == "ok"
        assert result.details["note"] == "simplified_check"
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, health_service):
        """Test getting overall health status"""
        with patch.object(health_service, 'check_database') as mock_db, \
             patch.object(health_service, 'check_redis') as mock_redis, \
             patch.object(health_service, 'check_storage') as mock_storage:
            
            # Mock healthy responses
            mock_db.return_value = ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=10.0,
                details={"connection": "ok"}
            )
            mock_redis.return_value = ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=5.0,
                details={"connection": "ok"}
            )
            mock_storage.return_value = ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=15.0,
                details={"connection": "ok"}
            )
            
            result = await health_service.get_health_status()
            
            assert len(result) == 3
            assert "database" in result
            assert "redis" in result
            assert "storage" in result
            assert all(service.status == ServiceStatus.HEALTHY for service in result.values())
    
    def test_determine_overall_status(self, health_service):
        """Test determining overall status from individual services"""
        # All healthy
        services = {
            "service1": ServiceHealth(status=ServiceStatus.HEALTHY),
            "service2": ServiceHealth(status=ServiceStatus.HEALTHY),
        }
        assert health_service.determine_overall_status(services) == ServiceStatus.HEALTHY
        
        # One degraded
        services["service1"] = ServiceHealth(status=ServiceStatus.DEGRADED)
        assert health_service.determine_overall_status(services) == ServiceStatus.DEGRADED
        
        # One unhealthy
        services["service1"] = ServiceHealth(status=ServiceStatus.UNHEALTHY)
        assert health_service.determine_overall_status(services) == ServiceStatus.UNHEALTHY
    
    def test_get_uptime(self, health_service):
        """Test uptime calculation"""
        uptime = health_service.get_uptime()
        assert uptime >= 0
        assert isinstance(uptime, float)