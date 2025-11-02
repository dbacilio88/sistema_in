"""
Data storage management module for traffic analysis system.

This module provides comprehensive data storage capabilities including:
- Historical data management
- Evidence file storage
- Media file handling
- Database operations
- Cloud storage integration
"""

import os
import time
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, BinaryIO
from pathlib import Path
import json
import pickle
import gzip
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
import threading
from enum import Enum
import uuid

import numpy as np
import cv2
from PIL import Image
import boto3
from botocore.exceptions import ClientError
import redis
import psycopg2
from psycopg2.extras import RealDictCursor


logger = logging.getLogger(__name__)


class StorageType(Enum):
    """Storage type enumeration."""
    LOCAL = "local"
    S3 = "s3"
    MINIO = "minio"
    DATABASE = "database"
    CACHE = "cache"


class DataType(Enum):
    """Data type enumeration."""
    IMAGE = "image"
    VIDEO = "video"
    JSON = "json"
    BINARY = "binary"
    TEXT = "text"
    METADATA = "metadata"


@dataclass
class StorageConfig:
    """Storage configuration."""
    # Local storage
    local_base_path: str = "/data/traffic_analysis"
    max_local_size_gb: float = 100.0
    
    # Database configuration
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "traffic_system"
    db_user: str = "admin"
    db_password: str = "password"
    
    # S3/MinIO configuration
    s3_endpoint: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_bucket: str = "traffic-evidence"
    s3_region: str = "us-east-1"
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Retention policies
    image_retention_days: int = 90
    video_retention_days: int = 30
    metadata_retention_days: int = 365
    
    # Performance settings
    compression_enabled: bool = True
    parallel_uploads: int = 4
    chunk_size_mb: int = 10


@dataclass
class StorageMetadata:
    """Storage metadata for files and data."""
    id: str
    storage_type: StorageType
    data_type: DataType
    file_path: str
    file_size: int
    checksum: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    tags: Optional[Dict[str, str]] = None
    compressed: bool = False
    encrypted: bool = False


@dataclass
class ViolationRecord:
    """Complete violation record for storage."""
    violation_id: str
    device_id: str
    violation_type: str
    timestamp: datetime
    
    # Detection data
    vehicle_bbox: List[int]
    license_plate: Optional[str]
    vehicle_class: str
    confidence: float
    
    # Analysis data
    speed_kmh: Optional[float]
    speed_limit: Optional[float]
    trajectory: List[Dict[str, Any]]
    
    # Evidence
    image_path: str
    video_segment_path: Optional[str]
    
    # Metadata
    camera_info: Dict[str, Any]
    processing_time_ms: float
    model_versions: Dict[str, str]


class LocalStorageManager:
    """Local file system storage manager."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.base_path = Path(config.local_base_path)
        self.executor = ThreadPoolExecutor(max_workers=config.parallel_uploads)
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            self.base_path / "images",
            self.base_path / "videos", 
            self.base_path / "metadata",
            self.base_path / "temp",
            self.base_path / "archive"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _get_file_path(self, file_id: str, data_type: DataType, extension: str = None) -> Path:
        """Generate file path for storage."""
        # Organize by date and type
        date_str = datetime.now().strftime("%Y/%m/%d")
        type_dir = data_type.value + "s"
        
        if extension:
            filename = f"{file_id}.{extension}"
        else:
            filename = file_id
            
        return self.base_path / type_dir / date_str / filename
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def store_image(self, image: np.ndarray, file_id: str, 
                   metadata: Optional[Dict] = None) -> StorageMetadata:
        """Store image to local storage."""
        file_path = self._get_file_path(file_id, DataType.IMAGE, "jpg")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save image
        cv2.imwrite(str(file_path), image)
        
        # Compress if enabled
        if self.config.compression_enabled:
            self._compress_file(file_path)
            file_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        # Calculate metadata
        file_size = file_path.stat().st_size
        checksum = self._calculate_checksum(file_path)
        
        storage_metadata = StorageMetadata(
            id=file_id,
            storage_type=StorageType.LOCAL,
            data_type=DataType.IMAGE,
            file_path=str(file_path),
            file_size=file_size,
            checksum=checksum,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.config.image_retention_days),
            tags=metadata,
            compressed=self.config.compression_enabled
        )
        
        logger.info(f"Stored image {file_id} at {file_path}")
        return storage_metadata
    
    def store_video_segment(self, video_data: bytes, file_id: str,
                           duration_seconds: float) -> StorageMetadata:
        """Store video segment to local storage."""
        file_path = self._get_file_path(file_id, DataType.VIDEO, "mp4")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write video data
        with open(file_path, "wb") as f:
            f.write(video_data)
        
        # Compress if enabled
        if self.config.compression_enabled:
            self._compress_file(file_path)
            file_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        file_size = file_path.stat().st_size
        checksum = self._calculate_checksum(file_path)
        
        storage_metadata = StorageMetadata(
            id=file_id,
            storage_type=StorageType.LOCAL,
            data_type=DataType.VIDEO,
            file_path=str(file_path),
            file_size=file_size,
            checksum=checksum,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.config.video_retention_days),
            tags={"duration_seconds": str(duration_seconds)},
            compressed=self.config.compression_enabled
        )
        
        logger.info(f"Stored video segment {file_id} at {file_path}")
        return storage_metadata
    
    def store_metadata(self, data: Dict[str, Any], file_id: str) -> StorageMetadata:
        """Store metadata as JSON."""
        file_path = self._get_file_path(file_id, DataType.METADATA, "json")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        # Compress if enabled
        if self.config.compression_enabled:
            self._compress_file(file_path)
            file_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        file_size = file_path.stat().st_size
        checksum = self._calculate_checksum(file_path)
        
        storage_metadata = StorageMetadata(
            id=file_id,
            storage_type=StorageType.LOCAL,
            data_type=DataType.METADATA,
            file_path=str(file_path),
            file_size=file_size,
            checksum=checksum,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.config.metadata_retention_days),
            compressed=self.config.compression_enabled
        )
        
        logger.info(f"Stored metadata {file_id} at {file_path}")
        return storage_metadata
    
    def _compress_file(self, file_path: Path):
        """Compress file using gzip."""
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove original file
        file_path.unlink()
    
    def retrieve_file(self, file_id: str, storage_metadata: StorageMetadata) -> bytes:
        """Retrieve file from local storage."""
        file_path = Path(storage_metadata.file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file
        if storage_metadata.compressed:
            with gzip.open(file_path, 'rb') as f:
                data = f.read()
        else:
            with open(file_path, 'rb') as f:
                data = f.read()
        
        # Verify checksum
        calculated_checksum = hashlib.sha256(data).hexdigest()
        if calculated_checksum != storage_metadata.checksum:
            logger.warning(f"Checksum mismatch for {file_id}")
        
        return data
    
    def delete_file(self, storage_metadata: StorageMetadata) -> bool:
        """Delete file from local storage."""
        file_path = Path(storage_metadata.file_path)
        
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file {storage_metadata.id}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {storage_metadata.id}: {e}")
            return False
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        total_size = 0
        file_count = 0
        type_sizes = {}
        
        for data_type in DataType:
            type_dir = self.base_path / (data_type.value + "s")
            if type_dir.exists():
                type_size = sum(f.stat().st_size for f in type_dir.rglob("*") if f.is_file())
                type_sizes[data_type.value] = type_size
                total_size += type_size
                file_count += len(list(type_dir.rglob("*")))
        
        usage_percentage = (total_size / (self.config.max_local_size_gb * 1024**3)) * 100
        
        return {
            "total_size_bytes": total_size,
            "total_size_gb": total_size / (1024**3),
            "file_count": file_count,
            "usage_percentage": usage_percentage,
            "by_type": type_sizes,
            "max_size_gb": self.config.max_local_size_gb
        }
    
    def cleanup_expired_files(self) -> Dict[str, int]:
        """Clean up expired files based on retention policies."""
        deleted_counts = {"images": 0, "videos": 0, "metadata": 0}
        now = datetime.now()
        
        # Define retention periods
        retention_policies = {
            "images": timedelta(days=self.config.image_retention_days),
            "videos": timedelta(days=self.config.video_retention_days),
            "metadata": timedelta(days=self.config.metadata_retention_days)
        }
        
        for data_type, retention_period in retention_policies.items():
            type_dir = self.base_path / data_type
            if not type_dir.exists():
                continue
                
            cutoff_time = now - retention_period
            
            for file_path in type_dir.rglob("*"):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                            deleted_counts[data_type] += 1
                            logger.debug(f"Deleted expired file: {file_path}")
                        except Exception as e:
                            logger.error(f"Error deleting expired file {file_path}: {e}")
        
        total_deleted = sum(deleted_counts.values())
        logger.info(f"Cleanup completed: {total_deleted} files deleted")
        
        return deleted_counts


class CloudStorageManager:
    """Cloud storage manager for S3/MinIO."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.client = self._create_client()
        self.executor = ThreadPoolExecutor(max_workers=config.parallel_uploads)
        
    def _create_client(self):
        """Create S3/MinIO client."""
        session = boto3.Session(
            aws_access_key_id=self.config.s3_access_key,
            aws_secret_access_key=self.config.s3_secret_key
        )
        
        client_config = {}
        if self.config.s3_endpoint:
            client_config['endpoint_url'] = self.config.s3_endpoint
            
        return session.client('s3', region_name=self.config.s3_region, **client_config)
    
    def _generate_key(self, file_id: str, data_type: DataType, extension: str = None) -> str:
        """Generate S3 key for file."""
        date_str = datetime.now().strftime("%Y/%m/%d")
        type_prefix = data_type.value
        
        if extension:
            filename = f"{file_id}.{extension}"
        else:
            filename = file_id
            
        return f"{type_prefix}/{date_str}/{filename}"
    
    async def upload_file_async(self, data: bytes, file_id: str, data_type: DataType,
                               metadata: Optional[Dict] = None) -> StorageMetadata:
        """Upload file to cloud storage asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._upload_file_sync, 
            data, file_id, data_type, metadata
        )
    
    def _upload_file_sync(self, data: bytes, file_id: str, data_type: DataType,
                         metadata: Optional[Dict] = None) -> StorageMetadata:
        """Upload file to cloud storage synchronously."""
        # Determine content type and extension
        if data_type == DataType.IMAGE:
            content_type = "image/jpeg"
            extension = "jpg"
        elif data_type == DataType.VIDEO:
            content_type = "video/mp4"
            extension = "mp4"
        elif data_type == DataType.JSON:
            content_type = "application/json"
            extension = "json"
        else:
            content_type = "application/octet-stream"
            extension = "bin"
        
        key = self._generate_key(file_id, data_type, extension)
        
        # Compress if enabled
        if self.config.compression_enabled:
            data = gzip.compress(data)
            key += ".gz"
            content_type = "application/gzip"
        
        # Prepare metadata
        s3_metadata = {
            "file-id": file_id,
            "data-type": data_type.value,
            "created-at": datetime.now().isoformat()
        }
        
        if metadata:
            for k, v in metadata.items():
                s3_metadata[f"custom-{k}"] = str(v)
        
        # Upload to S3
        try:
            self.client.put_object(
                Bucket=self.config.s3_bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                Metadata=s3_metadata
            )
            
            # Calculate checksum
            checksum = hashlib.sha256(data).hexdigest()
            
            storage_metadata = StorageMetadata(
                id=file_id,
                storage_type=StorageType.S3,
                data_type=data_type,
                file_path=key,
                file_size=len(data),
                checksum=checksum,
                created_at=datetime.now(),
                tags=metadata,
                compressed=self.config.compression_enabled
            )
            
            logger.info(f"Uploaded {file_id} to S3: {key}")
            return storage_metadata
            
        except ClientError as e:
            logger.error(f"Failed to upload {file_id} to S3: {e}")
            raise
    
    def download_file(self, storage_metadata: StorageMetadata) -> bytes:
        """Download file from cloud storage."""
        try:
            response = self.client.get_object(
                Bucket=self.config.s3_bucket,
                Key=storage_metadata.file_path
            )
            
            data = response['Body'].read()
            
            # Decompress if needed
            if storage_metadata.compressed:
                data = gzip.decompress(data)
            
            # Verify checksum
            calculated_checksum = hashlib.sha256(data).hexdigest()
            if calculated_checksum != storage_metadata.checksum:
                logger.warning(f"Checksum mismatch for {storage_metadata.id}")
            
            return data
            
        except ClientError as e:
            logger.error(f"Failed to download {storage_metadata.id} from S3: {e}")
            raise
    
    def delete_file(self, storage_metadata: StorageMetadata) -> bool:
        """Delete file from cloud storage."""
        try:
            self.client.delete_object(
                Bucket=self.config.s3_bucket,
                Key=storage_metadata.file_path
            )
            
            logger.info(f"Deleted {storage_metadata.id} from S3")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete {storage_metadata.id} from S3: {e}")
            return False
    
    def generate_presigned_url(self, storage_metadata: StorageMetadata, 
                              expires_in: int = 3600) -> str:
        """Generate presigned URL for file access."""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.config.s3_bucket,
                    'Key': storage_metadata.file_path
                },
                ExpiresIn=expires_in
            )
            
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {storage_metadata.id}: {e}")
            raise


class DatabaseManager:
    """Database manager for violation records and metadata."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.connection_pool = []
        self._initialize_schema()
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(
            host=self.config.db_host,
            port=self.config.db_port,
            database=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password,
            cursor_factory=RealDictCursor
        )
    
    def _initialize_schema(self):
        """Initialize database schema."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS violation_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            violation_id VARCHAR(100) UNIQUE NOT NULL,
            device_id VARCHAR(50) NOT NULL,
            violation_type VARCHAR(50) NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            
            vehicle_bbox INTEGER[] NOT NULL,
            license_plate VARCHAR(20),
            vehicle_class VARCHAR(50) NOT NULL,
            confidence REAL NOT NULL,
            
            speed_kmh REAL,
            speed_limit REAL,
            trajectory JSONB,
            
            image_path VARCHAR(500) NOT NULL,
            video_segment_path VARCHAR(500),
            
            camera_info JSONB,
            processing_time_ms REAL NOT NULL,
            model_versions JSONB,
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_violation_device_time 
        ON violation_records(device_id, timestamp);
        
        CREATE INDEX IF NOT EXISTS idx_violation_type 
        ON violation_records(violation_type);
        
        CREATE INDEX IF NOT EXISTS idx_violation_timestamp 
        ON violation_records(timestamp);
        
        CREATE TABLE IF NOT EXISTS storage_metadata (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            file_id VARCHAR(100) UNIQUE NOT NULL,
            storage_type VARCHAR(20) NOT NULL,
            data_type VARCHAR(20) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size BIGINT NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE,
            tags JSONB,
            compressed BOOLEAN DEFAULT FALSE,
            encrypted BOOLEAN DEFAULT FALSE
        );
        
        CREATE INDEX IF NOT EXISTS idx_storage_file_id 
        ON storage_metadata(file_id);
        
        CREATE INDEX IF NOT EXISTS idx_storage_expires 
        ON storage_metadata(expires_at);
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(schema_sql)
                    conn.commit()
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise
    
    def store_violation_record(self, record: ViolationRecord) -> str:
        """Store violation record in database."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO violation_records (
                            violation_id, device_id, violation_type, timestamp,
                            vehicle_bbox, license_plate, vehicle_class, confidence,
                            speed_kmh, speed_limit, trajectory,
                            image_path, video_segment_path,
                            camera_info, processing_time_ms, model_versions
                        ) VALUES (
                            %(violation_id)s, %(device_id)s, %(violation_type)s, %(timestamp)s,
                            %(vehicle_bbox)s, %(license_plate)s, %(vehicle_class)s, %(confidence)s,
                            %(speed_kmh)s, %(speed_limit)s, %(trajectory)s,
                            %(image_path)s, %(video_segment_path)s,
                            %(camera_info)s, %(processing_time_ms)s, %(model_versions)s
                        ) RETURNING id
                    """, asdict(record))
                    
                    record_id = cursor.fetchone()['id']
                    conn.commit()
                    
            logger.info(f"Stored violation record {record.violation_id}")
            return str(record_id)
            
        except Exception as e:
            logger.error(f"Failed to store violation record {record.violation_id}: {e}")
            raise
    
    def store_storage_metadata(self, metadata: StorageMetadata) -> str:
        """Store storage metadata in database."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO storage_metadata (
                            file_id, storage_type, data_type, file_path,
                            file_size, checksum, created_at, expires_at,
                            tags, compressed, encrypted
                        ) VALUES (
                            %(file_id)s, %(storage_type)s, %(data_type)s, %(file_path)s,
                            %(file_size)s, %(checksum)s, %(created_at)s, %(expires_at)s,
                            %(tags)s, %(compressed)s, %(encrypted)s
                        ) RETURNING id
                    """, {
                        'file_id': metadata.id,
                        'storage_type': metadata.storage_type.value,
                        'data_type': metadata.data_type.value,
                        'file_path': metadata.file_path,
                        'file_size': metadata.file_size,
                        'checksum': metadata.checksum,
                        'created_at': metadata.created_at,
                        'expires_at': metadata.expires_at,
                        'tags': json.dumps(metadata.tags) if metadata.tags else None,
                        'compressed': metadata.compressed,
                        'encrypted': metadata.encrypted
                    })
                    
                    record_id = cursor.fetchone()['id']
                    conn.commit()
                    
            logger.info(f"Stored storage metadata for {metadata.id}")
            return str(record_id)
            
        except Exception as e:
            logger.error(f"Failed to store storage metadata for {metadata.id}: {e}")
            raise
    
    def get_violation_records(self, device_id: Optional[str] = None,
                             violation_type: Optional[str] = None,
                             start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve violation records with filters."""
        conditions = []
        params = {}
        
        if device_id:
            conditions.append("device_id = %(device_id)s")
            params['device_id'] = device_id
        
        if violation_type:
            conditions.append("violation_type = %(violation_type)s")
            params['violation_type'] = violation_type
        
        if start_time:
            conditions.append("timestamp >= %(start_time)s")
            params['start_time'] = start_time
        
        if end_time:
            conditions.append("timestamp <= %(end_time)s")
            params['end_time'] = end_time
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT * FROM violation_records
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT %(limit)s
        """
        params['limit'] = limit
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    records = cursor.fetchall()
                    
            return [dict(record) for record in records]
            
        except Exception as e:
            logger.error(f"Failed to retrieve violation records: {e}")
            raise
    
    def get_storage_metadata(self, file_id: str) -> Optional[StorageMetadata]:
        """Retrieve storage metadata by file ID."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM storage_metadata WHERE file_id = %s
                    """, (file_id,))
                    
                    record = cursor.fetchone()
                    
            if not record:
                return None
            
            return StorageMetadata(
                id=record['file_id'],
                storage_type=StorageType(record['storage_type']),
                data_type=DataType(record['data_type']),
                file_path=record['file_path'],
                file_size=record['file_size'],
                checksum=record['checksum'],
                created_at=record['created_at'],
                expires_at=record['expires_at'],
                tags=json.loads(record['tags']) if record['tags'] else None,
                compressed=record['compressed'],
                encrypted=record['encrypted']
            )
            
        except Exception as e:
            logger.error(f"Failed to retrieve storage metadata for {file_id}: {e}")
            raise


class CacheManager:
    """Redis cache manager for fast data access."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            decode_responses=False  # For binary data
        )
        self.default_ttl = 3600  # 1 hour
    
    def store_processed_frame(self, frame_id: str, processed_data: Dict[str, Any],
                             ttl: Optional[int] = None) -> bool:
        """Store processed frame data in cache."""
        try:
            key = f"frame:{frame_id}"
            data = pickle.dumps(processed_data)
            
            result = self.redis_client.setex(
                key, 
                ttl or self.default_ttl, 
                data
            )
            
            if result:
                logger.debug(f"Cached processed frame {frame_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to cache frame {frame_id}: {e}")
            return False
    
    def get_processed_frame(self, frame_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve processed frame data from cache."""
        try:
            key = f"frame:{frame_id}"
            data = self.redis_client.get(key)
            
            if data:
                return pickle.loads(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached frame {frame_id}: {e}")
            return None
    
    def store_detection_results(self, image_hash: str, detections: List[Dict],
                               ttl: Optional[int] = None) -> bool:
        """Store detection results for duplicate image detection."""
        try:
            key = f"detection:{image_hash}"
            data = pickle.dumps(detections)
            
            result = self.redis_client.setex(
                key,
                ttl or self.default_ttl,
                data
            )
            
            if result:
                logger.debug(f"Cached detection results for {image_hash}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to cache detection results for {image_hash}: {e}")
            return False
    
    def get_detection_results(self, image_hash: str) -> Optional[List[Dict]]:
        """Retrieve cached detection results."""
        try:
            key = f"detection:{image_hash}"
            data = self.redis_client.get(key)
            
            if data:
                return pickle.loads(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached detection results for {image_hash}: {e}")
            return None
    
    def increment_counter(self, counter_name: str, increment: int = 1) -> int:
        """Increment a counter and return new value."""
        try:
            key = f"counter:{counter_name}"
            return self.redis_client.incrby(key, increment)
        except Exception as e:
            logger.error(f"Failed to increment counter {counter_name}: {e}")
            return 0
    
    def set_system_metric(self, metric_name: str, value: float,
                         ttl: Optional[int] = None) -> bool:
        """Store system metric value."""
        try:
            key = f"metric:{metric_name}"
            result = self.redis_client.setex(
                key,
                ttl or 300,  # 5 minutes default
                str(value)
            )
            return result
        except Exception as e:
            logger.error(f"Failed to store metric {metric_name}: {e}")
            return False
    
    def get_system_metric(self, metric_name: str) -> Optional[float]:
        """Retrieve system metric value."""
        try:
            key = f"metric:{metric_name}"
            value = self.redis_client.get(key)
            
            if value:
                return float(value.decode())
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve metric {metric_name}: {e}")
            return None
    
    def clear_cache(self, pattern: str = None) -> int:
        """Clear cache entries matching pattern."""
        try:
            if pattern:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                return self.redis_client.flushdb()
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0