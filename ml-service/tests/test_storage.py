"""
Comprehensive test suite for storage module.

Tests all storage components including managers, services, and utilities.
"""

import pytest
import asyncio
import tempfile
import shutil
import os
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
import json
import gzip
import hashlib

import numpy as np
import cv2
import redis
import psycopg2

from ..storage_manager import (
    StorageConfig, StorageType, DataType, StorageMetadata, ViolationRecord,
    LocalStorageManager, CloudStorageManager, DatabaseManager, CacheManager
)
from ..storage_service import StorageService, StorageStrategy, ArchiveManager
from ..data_utils import (
    DataValidator, DataLifecycleManager, DataMigrationManager,
    DataAnalyzer, DataExporter
)


class TestStorageConfig:
    """Test storage configuration."""
    
    def test_default_config(self):
        """Test default storage configuration."""
        config = StorageConfig()
        
        assert config.local_base_path == "/data/traffic_analysis"
        assert config.max_local_size_gb == 100.0
        assert config.image_retention_days == 90
        assert config.video_retention_days == 30
        assert config.compression_enabled is True
    
    def test_custom_config(self):
        """Test custom storage configuration."""
        config = StorageConfig(
            local_base_path="/custom/path",
            max_local_size_gb=200.0,
            image_retention_days=180,
            compression_enabled=False
        )
        
        assert config.local_base_path == "/custom/path"
        assert config.max_local_size_gb == 200.0
        assert config.image_retention_days == 180
        assert config.compression_enabled is False


class TestLocalStorageManager:
    """Test local storage manager."""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary storage configuration."""
        temp_dir = tempfile.mkdtemp()
        config = StorageConfig(
            local_base_path=temp_dir,
            compression_enabled=False  # Disable for easier testing
        )
        yield config
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def storage_manager(self, temp_config):
        """Create local storage manager."""
        return LocalStorageManager(temp_config)
    
    @pytest.fixture
    def test_image(self):
        """Create test image."""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_initialization(self, storage_manager, temp_config):
        """Test storage manager initialization."""
        base_path = Path(temp_config.local_base_path)
        
        # Check directories were created
        assert (base_path / "images").exists()
        assert (base_path / "videos").exists()
        assert (base_path / "metadata").exists()
        assert (base_path / "temp").exists()
        assert (base_path / "archive").exists()
    
    def test_store_image(self, storage_manager, test_image):
        """Test image storage."""
        file_id = "test_image_001"
        metadata = {"device_id": "cam_001", "timestamp": "2025-11-01T10:00:00"}
        
        storage_metadata = storage_manager.store_image(test_image, file_id, metadata)
        
        assert storage_metadata.id == file_id
        assert storage_metadata.storage_type == StorageType.LOCAL
        assert storage_metadata.data_type == DataType.IMAGE
        assert storage_metadata.file_size > 0
        assert storage_metadata.checksum is not None
        assert storage_metadata.tags == metadata
        
        # Verify file exists
        file_path = Path(storage_metadata.file_path)
        assert file_path.exists()
    
    def test_store_video_segment(self, storage_manager):
        """Test video segment storage."""
        video_data = b"fake_video_data" * 1000  # Simulate video data
        file_id = "test_video_001"
        duration = 10.5
        
        storage_metadata = storage_manager.store_video_segment(video_data, file_id, duration)
        
        assert storage_metadata.id == file_id
        assert storage_metadata.storage_type == StorageType.LOCAL
        assert storage_metadata.data_type == DataType.VIDEO
        assert storage_metadata.file_size == len(video_data)
        assert storage_metadata.tags["duration_seconds"] == str(duration)
        
        # Verify file exists
        file_path = Path(storage_metadata.file_path)
        assert file_path.exists()
    
    def test_store_metadata(self, storage_manager):
        """Test metadata storage."""
        metadata = {
            "violation_id": "V001",
            "device_id": "cam_001",
            "detections": [{"bbox": [100, 100, 200, 200], "confidence": 0.95}],
            "timestamp": datetime.now().isoformat()
        }
        file_id = "test_metadata_001"
        
        storage_metadata = storage_manager.store_metadata(metadata, file_id)
        
        assert storage_metadata.id == file_id
        assert storage_metadata.storage_type == StorageType.LOCAL
        assert storage_metadata.data_type == DataType.METADATA
        
        # Verify file exists and content is correct
        file_path = Path(storage_metadata.file_path)
        assert file_path.exists()
        
        with open(file_path, 'r') as f:
            stored_data = json.load(f)
        
        assert stored_data == metadata
    
    def test_retrieve_file(self, storage_manager, test_image):
        """Test file retrieval."""
        file_id = "test_retrieve_001"
        
        # Store image first
        storage_metadata = storage_manager.store_image(test_image, file_id)
        
        # Retrieve image
        retrieved_data = storage_manager.retrieve_file(file_id, storage_metadata)
        
        # Verify checksum matches
        calculated_checksum = hashlib.sha256(retrieved_data).hexdigest()
        assert calculated_checksum == storage_metadata.checksum
        
        # Verify image can be decoded
        nparr = np.frombuffer(retrieved_data, np.uint8)
        decoded_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        assert decoded_image is not None
        assert decoded_image.shape == test_image.shape
    
    def test_delete_file(self, storage_manager, test_image):
        """Test file deletion."""
        file_id = "test_delete_001"
        
        # Store image first
        storage_metadata = storage_manager.store_image(test_image, file_id)
        file_path = Path(storage_metadata.file_path)
        
        # Verify file exists
        assert file_path.exists()
        
        # Delete file
        success = storage_manager.delete_file(storage_metadata)
        
        assert success is True
        assert not file_path.exists()
    
    def test_get_storage_usage(self, storage_manager, test_image):
        """Test storage usage calculation."""
        # Store several files
        for i in range(3):
            storage_manager.store_image(test_image, f"usage_test_{i}")
        
        usage = storage_manager.get_storage_usage()
        
        assert "total_size_bytes" in usage
        assert "total_size_gb" in usage
        assert "file_count" in usage
        assert "usage_percentage" in usage
        assert "by_type" in usage
        assert usage["total_size_bytes"] > 0
        assert usage["file_count"] >= 3
    
    def test_compression(self, temp_config):
        """Test file compression."""
        temp_config.compression_enabled = True
        storage_manager = LocalStorageManager(temp_config)
        
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        file_id = "test_compression_001"
        
        storage_metadata = storage_manager.store_image(test_image, file_id)
        
        assert storage_metadata.compressed is True
        assert storage_metadata.file_path.endswith('.gz')
        
        # Verify file exists and is compressed
        file_path = Path(storage_metadata.file_path)
        assert file_path.exists()
        
        # Verify can retrieve and decompress
        retrieved_data = storage_manager.retrieve_file(file_id, storage_metadata)
        assert len(retrieved_data) > 0


class TestCloudStorageManager:
    """Test cloud storage manager."""
    
    @pytest.fixture
    def cloud_config(self):
        """Create cloud storage configuration."""
        return StorageConfig(
            s3_endpoint="http://localhost:9000",
            s3_access_key="test_access_key",
            s3_secret_key="test_secret_key",
            s3_bucket="test-bucket"
        )
    
    @pytest.fixture
    def mock_s3_client(self):
        """Mock S3 client."""
        with patch('boto3.Session') as mock_session:
            mock_client = Mock()
            mock_session.return_value.client.return_value = mock_client
            yield mock_client
    
    def test_initialization(self, cloud_config, mock_s3_client):
        """Test cloud storage manager initialization."""
        manager = CloudStorageManager(cloud_config)
        
        assert manager.config == cloud_config
        assert manager.client == mock_s3_client
    
    @pytest.mark.asyncio
    async def test_upload_file_async(self, cloud_config, mock_s3_client):
        """Test async file upload."""
        manager = CloudStorageManager(cloud_config)
        
        test_data = b"test file content"
        file_id = "test_upload_001"
        
        # Mock successful upload
        mock_s3_client.put_object.return_value = None
        
        storage_metadata = await manager.upload_file_async(
            test_data, file_id, DataType.IMAGE
        )
        
        assert storage_metadata.id == file_id
        assert storage_metadata.storage_type == StorageType.S3
        assert storage_metadata.data_type == DataType.IMAGE
        assert storage_metadata.file_size == len(test_data)
        
        # Verify S3 client was called
        mock_s3_client.put_object.assert_called_once()
    
    def test_download_file(self, cloud_config, mock_s3_client):
        """Test file download."""
        manager = CloudStorageManager(cloud_config)
        
        test_data = b"test file content"
        checksum = hashlib.sha256(test_data).hexdigest()
        
        storage_metadata = StorageMetadata(
            id="test_download_001",
            storage_type=StorageType.S3,
            data_type=DataType.IMAGE,
            file_path="test/path.jpg",
            file_size=len(test_data),
            checksum=checksum,
            created_at=datetime.now()
        )
        
        # Mock S3 response
        mock_response = {
            'Body': Mock()
        }
        mock_response['Body'].read.return_value = test_data
        mock_s3_client.get_object.return_value = mock_response
        
        downloaded_data = manager.download_file(storage_metadata)
        
        assert downloaded_data == test_data
        mock_s3_client.get_object.assert_called_once()
    
    def test_generate_presigned_url(self, cloud_config, mock_s3_client):
        """Test presigned URL generation."""
        manager = CloudStorageManager(cloud_config)
        
        storage_metadata = StorageMetadata(
            id="test_url_001",
            storage_type=StorageType.S3,
            data_type=DataType.IMAGE,
            file_path="test/path.jpg",
            file_size=1024,
            checksum="test_checksum",
            created_at=datetime.now()
        )
        
        expected_url = "https://test-bucket.s3.amazonaws.com/test/path.jpg?signature=abc123"
        mock_s3_client.generate_presigned_url.return_value = expected_url
        
        url = manager.generate_presigned_url(storage_metadata, expires_in=3600)
        
        assert url == expected_url
        mock_s3_client.generate_presigned_url.assert_called_once()


class TestCacheManager:
    """Test cache manager."""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        with patch('redis.Redis') as mock_redis_class:
            mock_client = Mock()
            mock_redis_class.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def cache_manager(self, mock_redis):
        """Create cache manager with mocked Redis."""
        config = StorageConfig()
        return CacheManager(config)
    
    def test_store_processed_frame(self, cache_manager, mock_redis):
        """Test processed frame caching."""
        frame_id = "frame_001"
        processed_data = {
            "detections": [{"bbox": [100, 100, 200, 200], "confidence": 0.95}],
            "timestamp": time.time()
        }
        
        mock_redis.setex.return_value = True
        
        result = cache_manager.store_processed_frame(frame_id, processed_data)
        
        assert result is True
        mock_redis.setex.assert_called_once()
        
        # Check key format
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"frame:{frame_id}"
    
    def test_get_processed_frame(self, cache_manager, mock_redis):
        """Test processed frame retrieval."""
        frame_id = "frame_001"
        test_data = {"detections": [], "timestamp": time.time()}
        
        # Mock Redis returning pickled data
        import pickle
        mock_redis.get.return_value = pickle.dumps(test_data)
        
        retrieved_data = cache_manager.get_processed_frame(frame_id)
        
        assert retrieved_data == test_data
        mock_redis.get.assert_called_once_with(f"frame:{frame_id}")
    
    def test_increment_counter(self, cache_manager, mock_redis):
        """Test counter increment."""
        counter_name = "processed_frames"
        
        mock_redis.incrby.return_value = 42
        
        result = cache_manager.increment_counter(counter_name, 5)
        
        assert result == 42
        mock_redis.incrby.assert_called_once_with(f"counter:{counter_name}", 5)
    
    def test_system_metrics(self, cache_manager, mock_redis):
        """Test system metrics storage and retrieval."""
        metric_name = "cpu_usage"
        metric_value = 75.5
        
        # Test storing metric
        mock_redis.setex.return_value = True
        
        result = cache_manager.set_system_metric(metric_name, metric_value)
        assert result is True
        
        # Test retrieving metric
        mock_redis.get.return_value = str(metric_value).encode()
        
        retrieved_value = cache_manager.get_system_metric(metric_name)
        assert retrieved_value == metric_value


class TestDatabaseManager:
    """Test database manager."""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection."""
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_connect.return_value.__enter__.return_value = mock_conn
            yield mock_conn, mock_cursor
    
    @pytest.fixture
    def db_manager(self, mock_db_connection):
        """Create database manager with mocked connection."""
        config = StorageConfig()
        with patch.object(DatabaseManager, '_initialize_schema'):
            return DatabaseManager(config)
    
    @pytest.fixture
    def test_violation_record(self):
        """Create test violation record."""
        return ViolationRecord(
            violation_id="V001",
            device_id="cam_001",
            violation_type="speed",
            timestamp=datetime.now(),
            vehicle_bbox=[100, 100, 200, 200],
            license_plate="ABC123",
            vehicle_class="car",
            confidence=0.95,
            speed_kmh=85.0,
            speed_limit=60.0,
            trajectory=[{"x": 100, "y": 100, "timestamp": time.time()}],
            image_path="/path/to/image.jpg",
            video_segment_path="/path/to/video.mp4",
            camera_info={"location": "Main St", "angle": 45},
            processing_time_ms=150.0,
            model_versions={"detector": "yolov8", "tracker": "deepsort"}
        )
    
    def test_store_violation_record(self, db_manager, mock_db_connection, test_violation_record):
        """Test storing violation record."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_cursor.fetchone.return_value = {'id': 'record_uuid_123'}
        
        record_id = db_manager.store_violation_record(test_violation_record)
        
        assert record_id == 'record_uuid_123'
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    def test_get_violation_records(self, db_manager, mock_db_connection):
        """Test retrieving violation records."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Mock query results
        mock_records = [
            {
                'violation_id': 'V001',
                'device_id': 'cam_001',
                'violation_type': 'speed',
                'timestamp': datetime.now()
            },
            {
                'violation_id': 'V002',
                'device_id': 'cam_002',
                'violation_type': 'red_light',
                'timestamp': datetime.now()
            }
        ]
        mock_cursor.fetchall.return_value = mock_records
        
        records = db_manager.get_violation_records(device_id="cam_001", limit=100)
        
        assert len(records) == 2
        assert records[0]['violation_id'] == 'V001'
        mock_cursor.execute.assert_called_once()
    
    def test_store_storage_metadata(self, db_manager, mock_db_connection):
        """Test storing storage metadata."""
        mock_conn, mock_cursor = mock_db_connection
        
        metadata = StorageMetadata(
            id="file_001",
            storage_type=StorageType.LOCAL,
            data_type=DataType.IMAGE,
            file_path="/path/to/file.jpg",
            file_size=1024,
            checksum="abc123",
            created_at=datetime.now()
        )
        
        mock_cursor.fetchone.return_value = {'id': 'metadata_uuid_123'}
        
        record_id = db_manager.store_storage_metadata(metadata)
        
        assert record_id == 'metadata_uuid_123'
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()


class TestStorageService:
    """Test unified storage service."""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary storage configuration."""
        temp_dir = tempfile.mkdtemp()
        config = StorageConfig(
            local_base_path=temp_dir,
            compression_enabled=False
        )
        yield config
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_components(self):
        """Mock storage components."""
        with patch('src.storage.storage_service.LocalStorageManager') as mock_local, \
             patch('src.storage.storage_service.DatabaseManager') as mock_db, \
             patch('src.storage.storage_service.CacheManager') as mock_cache:
            
            yield mock_local, mock_db, mock_cache
    
    @pytest.fixture
    def storage_service(self, temp_config, mock_components):
        """Create storage service with mocked components."""
        mock_local, mock_db, mock_cache = mock_components
        
        service = StorageService(temp_config, StorageStrategy.LOCAL_ONLY)
        
        # Setup mock returns
        service.local_manager = mock_local.return_value
        service.db_manager = mock_db.return_value
        service.cache_manager = mock_cache.return_value
        
        return service
    
    @pytest.mark.asyncio
    async def test_store_image(self, storage_service):
        """Test image storage through service."""
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        file_id = "service_test_001"
        
        # Mock local manager response
        expected_metadata = StorageMetadata(
            id=file_id,
            storage_type=StorageType.LOCAL,
            data_type=DataType.IMAGE,
            file_path="/path/to/image.jpg",
            file_size=1024,
            checksum="abc123",
            created_at=datetime.now()
        )
        
        storage_service.local_manager.store_image.return_value = expected_metadata
        storage_service.cache_manager.get_processed_frame.return_value = None
        
        result = await storage_service.store_image(test_image, file_id)
        
        assert result.id == file_id
        storage_service.local_manager.store_image.assert_called_once()
        storage_service.db_manager.store_storage_metadata.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_file(self, storage_service):
        """Test file retrieval through service."""
        file_id = "retrieve_test_001"
        test_data = b"test file content"
        
        storage_metadata = StorageMetadata(
            id=file_id,
            storage_type=StorageType.LOCAL,
            data_type=DataType.IMAGE,
            file_path="/path/to/image.jpg",
            file_size=len(test_data),
            checksum=hashlib.sha256(test_data).hexdigest(),
            created_at=datetime.now()
        )
        
        # Mock database and local manager responses
        storage_service.db_manager.get_storage_metadata.return_value = storage_metadata
        storage_service.cache_manager.redis_client.get.return_value = None
        storage_service.local_manager.retrieve_file.return_value = test_data
        
        retrieved_data, metadata = await storage_service.retrieve_file(file_id)
        
        assert retrieved_data == test_data
        assert metadata == storage_metadata
        storage_service.db_manager.get_storage_metadata.assert_called_once_with(file_id)
        storage_service.local_manager.retrieve_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_violation_evidence(self, storage_service):
        """Test complete violation evidence storage."""
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        test_video = b"fake_video_data" * 1000
        
        violation_record = ViolationRecord(
            violation_id="V001",
            device_id="cam_001",
            violation_type="speed",
            timestamp=datetime.now(),
            vehicle_bbox=[100, 100, 200, 200],
            vehicle_class="car",
            confidence=0.95,
            image_path="",  # Will be set by method
            camera_info={},
            processing_time_ms=150.0,
            model_versions={}
        )
        
        # Mock storage responses
        image_metadata = StorageMetadata(
            id="violation_V001_evidence",
            storage_type=StorageType.LOCAL,
            data_type=DataType.IMAGE,
            file_path="/path/to/evidence.jpg",
            file_size=1024,
            checksum="image_checksum",
            created_at=datetime.now()
        )
        
        video_metadata = StorageMetadata(
            id="violation_V001_video",
            storage_type=StorageType.LOCAL,
            data_type=DataType.VIDEO,
            file_path="/path/to/video.mp4",
            file_size=len(test_video),
            checksum="video_checksum",
            created_at=datetime.now()
        )
        
        metadata_metadata = StorageMetadata(
            id="violation_V001_metadata",
            storage_type=StorageType.LOCAL,
            data_type=DataType.METADATA,
            file_path="/path/to/metadata.json",
            file_size=512,
            checksum="metadata_checksum",
            created_at=datetime.now()
        )
        
        # Setup mocks
        storage_service.cache_manager.get_processed_frame.return_value = None
        
        async def mock_store_image(image, file_id, metadata=None):
            return image_metadata
        
        async def mock_store_video_segment(video_data, file_id, duration):
            return video_metadata
        
        async def mock_store_metadata(data, file_id):
            return metadata_metadata
        
        storage_service.store_image = mock_store_image
        storage_service.store_video_segment = mock_store_video_segment
        storage_service.store_metadata = mock_store_metadata
        
        stored_files = await storage_service.store_violation_evidence(
            violation_record, test_image, test_video
        )
        
        assert "image" in stored_files
        assert "video" in stored_files
        assert "metadata" in stored_files
        assert stored_files["image"] == image_metadata
        assert stored_files["video"] == video_metadata
        assert stored_files["metadata"] == metadata_metadata
        
        # Verify violation record was updated
        assert violation_record.image_path == image_metadata.file_path
        assert violation_record.video_segment_path == video_metadata.file_path


class TestDataValidator:
    """Test data validation utilities."""
    
    @pytest.fixture
    def validator(self):
        """Create data validator."""
        return DataValidator()
    
    @pytest.fixture
    def valid_violation_record(self):
        """Create valid violation record for testing."""
        return ViolationRecord(
            violation_id="V001",
            device_id="cam_001",
            violation_type="speed",
            timestamp=datetime.now(),
            vehicle_bbox=[100, 100, 200, 200],
            license_plate="ABC123",
            vehicle_class="car",
            confidence=0.95,
            speed_kmh=75.0,
            speed_limit=60.0,
            trajectory=[],
            image_path="/path/to/image.jpg",
            camera_info={},
            processing_time_ms=150.0,
            model_versions={}
        )
    
    def test_validate_valid_record(self, validator, valid_violation_record):
        """Test validation of valid violation record."""
        result = validator.validate_violation_record(valid_violation_record)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["score"] > 0.7
    
    def test_validate_invalid_confidence(self, validator, valid_violation_record):
        """Test validation with invalid confidence."""
        valid_violation_record.confidence = 1.5  # Invalid confidence > 1.0
        
        result = validator.validate_violation_record(valid_violation_record)
        
        assert result["valid"] is False
        assert any("Confidence must be between 0.0 and 1.0" in error for error in result["errors"])
    
    def test_validate_invalid_bbox(self, validator, valid_violation_record):
        """Test validation with invalid bounding box."""
        valid_violation_record.vehicle_bbox = [200, 200, 100, 100]  # x1 > x2, y1 > y2
        
        result = validator.validate_violation_record(valid_violation_record)
        
        assert result["valid"] is False
        assert any("Invalid bounding box coordinates" in error for error in result["errors"])
    
    def test_validate_missing_field(self, validator):
        """Test validation with missing required field."""
        incomplete_record = ViolationRecord(
            violation_id="V001",
            device_id="cam_001",
            violation_type="speed",
            timestamp=datetime.now(),
            vehicle_bbox=[100, 100, 200, 200],
            vehicle_class="car",
            confidence=0.95,
            image_path="/path/to/image.jpg",
            camera_info={},
            processing_time_ms=150.0,
            model_versions={},
            # Missing some fields
            license_plate=None,
            speed_kmh=None,
            speed_limit=None,
            trajectory=None
        )
        
        result = validator.validate_violation_record(incomplete_record)
        
        # Should still be valid as these are optional fields
        assert result["valid"] is True
    
    def test_validate_image_data(self, validator):
        """Test image data validation."""
        # Create test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        result = validator._validate_image_data(test_image)
        
        assert result["valid"] is True
        assert result["metrics"]["width"] == 640
        assert result["metrics"]["height"] == 480
        assert result["metrics"]["channels"] == 3
        assert "mean_brightness" in result["metrics"]
        assert "blur_score" in result["metrics"]
    
    def test_validate_low_resolution_image(self, validator):
        """Test validation of low resolution image."""
        low_res_image = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
        
        result = validator._validate_image_data(low_res_image)
        
        assert result["valid"] is True  # Still valid, just with warnings
        assert any("Low resolution image" in warning for warning in result["warnings"])
    
    def test_validate_none_image(self, validator):
        """Test validation of None image."""
        result = validator._validate_image_data(None)
        
        assert result["valid"] is False
        assert any("Image is None" in error for error in result["errors"])


class TestDataLifecycleManager:
    """Test data lifecycle management."""
    
    @pytest.fixture
    def mock_storage_service(self):
        """Mock storage service."""
        return Mock(spec=StorageService)
    
    @pytest.fixture
    def lifecycle_manager(self, mock_storage_service):
        """Create data lifecycle manager."""
        return DataLifecycleManager(mock_storage_service)
    
    @pytest.mark.asyncio
    async def test_apply_retention_policies(self, lifecycle_manager):
        """Test applying retention policies."""
        with patch.object(lifecycle_manager, '_delete_old_files', return_value=10):
            result = await lifecycle_manager.apply_retention_policies()
            
            assert result["policies_applied"] > 0
            assert result["files_deleted"] >= 0
            assert isinstance(result["errors"], list)
    
    @pytest.mark.asyncio
    async def test_create_data_snapshot(self, lifecycle_manager, mock_storage_service):
        """Test creating data snapshot."""
        snapshot_id = "test_snapshot_001"
        
        # Mock violation records
        mock_violations = [
            {"violation_id": "V001", "timestamp": datetime.now()},
            {"violation_id": "V002", "timestamp": datetime.now()}
        ]
        mock_storage_service.get_violation_records.return_value = mock_violations
        
        # Mock storage metadata
        mock_metadata = StorageMetadata(
            id=f"snapshot_{snapshot_id}",
            storage_type=StorageType.LOCAL,
            data_type=DataType.METADATA,
            file_path="/path/to/snapshot.json",
            file_size=1024,
            checksum="snapshot_checksum",
            created_at=datetime.now()
        )
        mock_storage_service.store_metadata.return_value = mock_metadata
        
        result = await lifecycle_manager.create_data_snapshot(snapshot_id)
        
        assert result["snapshot_id"] == snapshot_id
        assert result["violation_records_count"] == 2
        assert result["snapshot_size_bytes"] == 1024
        assert "timestamp" in result
        
        mock_storage_service.get_violation_records.assert_called_once()
        mock_storage_service.store_metadata.assert_called_once()


def run_storage_tests():
    """Run all storage tests."""
    pytest.main([__file__, "-v", "--tb=short"])