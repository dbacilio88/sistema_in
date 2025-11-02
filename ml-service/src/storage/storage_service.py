"""
Unified storage service for traffic analysis system.

This module provides a high-level interface for all storage operations,
managing multiple storage backends and providing intelligent data placement.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from enum import Enum

import numpy as np
import cv2

from .storage_manager import (
    StorageConfig, StorageType, DataType, StorageMetadata, ViolationRecord,
    LocalStorageManager, CloudStorageManager, DatabaseManager, CacheManager
)


logger = logging.getLogger(__name__)


class StorageStrategy(Enum):
    """Storage strategy for data placement."""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    LOCAL_THEN_CLOUD = "local_then_cloud"
    CLOUD_WITH_CACHE = "cloud_with_cache"
    HYBRID = "hybrid"


class StorageService:
    """Unified storage service managing multiple storage backends."""
    
    def __init__(self, config: StorageConfig, strategy: StorageStrategy = StorageStrategy.HYBRID):
        self.config = config
        self.strategy = strategy
        
        # Initialize storage managers
        self.local_manager = LocalStorageManager(config)
        self.cache_manager = CacheManager(config)
        self.db_manager = DatabaseManager(config)
        
        # Initialize cloud manager if configured
        self.cloud_manager = None
        if config.s3_access_key and config.s3_secret_key:
            self.cloud_manager = CloudStorageManager(config)
        
        # Performance tracking
        self.operation_times = {}
        self.storage_stats = {
            "files_stored": 0,
            "files_retrieved": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        
        # Background tasks
        self.cleanup_task = None
        self.sync_task = None
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        # Cleanup task runs every hour
        self.cleanup_task = asyncio.create_task(self._periodic_cleanup())
        
        # Sync task runs every 30 minutes if cloud storage is available
        if self.cloud_manager:
            self.sync_task = asyncio.create_task(self._periodic_sync())
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired files."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                logger.info("Starting periodic cleanup")
                
                # Clean up local storage
                deleted_local = self.local_manager.cleanup_expired_files()
                
                # Clean up cache
                cache_cleared = self.cache_manager.clear_cache("frame:*")
                
                logger.info(f"Cleanup completed: local={deleted_local}, cache={cache_cleared}")
                
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    async def _periodic_sync(self):
        """Periodic synchronization between local and cloud storage."""
        while True:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                
                if self.strategy in [StorageStrategy.LOCAL_THEN_CLOUD, StorageStrategy.HYBRID]:
                    await self._sync_local_to_cloud()
                
            except Exception as e:
                logger.error(f"Error in periodic sync: {e}")
    
    async def _sync_local_to_cloud(self):
        """Sync local files to cloud storage."""
        logger.info("Starting local to cloud sync")
        
        # Get local storage usage
        usage = self.local_manager.get_storage_usage()
        
        # If usage is high, prioritize syncing older files
        if usage['usage_percentage'] > 80:
            await self._sync_oldest_files_to_cloud(limit=100)
    
    async def _sync_oldest_files_to_cloud(self, limit: int = 50):
        """Sync oldest local files to cloud storage."""
        # This would need to track file metadata to determine oldest files
        # For now, we'll implement a basic version
        pass
    
    def _calculate_image_hash(self, image: np.ndarray) -> str:
        """Calculate hash of image for duplicate detection."""
        # Convert to bytes and hash
        image_bytes = cv2.imencode('.jpg', image)[1].tobytes()
        return hashlib.sha256(image_bytes).hexdigest()
    
    def _get_storage_location(self, data_type: DataType, file_size: int) -> StorageType:
        """Determine optimal storage location based on strategy and file characteristics."""
        if self.strategy == StorageStrategy.LOCAL_ONLY:
            return StorageType.LOCAL
        
        elif self.strategy == StorageStrategy.CLOUD_ONLY:
            if self.cloud_manager:
                return StorageType.S3
            else:
                logger.warning("Cloud storage not configured, falling back to local")
                return StorageType.LOCAL
        
        elif self.strategy == StorageStrategy.LOCAL_THEN_CLOUD:
            # Check local storage capacity
            usage = self.local_manager.get_storage_usage()
            if usage['usage_percentage'] < 90:
                return StorageType.LOCAL
            elif self.cloud_manager:
                return StorageType.S3
            else:
                return StorageType.LOCAL
        
        elif self.strategy == StorageStrategy.CLOUD_WITH_CACHE:
            return StorageType.S3 if self.cloud_manager else StorageType.LOCAL
        
        elif self.strategy == StorageStrategy.HYBRID:
            # Large files (>10MB) go to cloud, small files stay local
            if file_size > 10 * 1024 * 1024 and self.cloud_manager:
                return StorageType.S3
            else:
                return StorageType.LOCAL
        
        return StorageType.LOCAL
    
    async def store_violation_evidence(self, violation_record: ViolationRecord,
                                     image: np.ndarray,
                                     video_segment: Optional[bytes] = None) -> Dict[str, StorageMetadata]:
        """Store complete violation evidence (image, video, metadata)."""
        start_time = time.time()
        stored_files = {}
        
        try:
            # Store main evidence image
            image_metadata = await self.store_image(
                image, 
                f"violation_{violation_record.violation_id}_evidence",
                metadata={
                    "violation_id": violation_record.violation_id,
                    "device_id": violation_record.device_id,
                    "violation_type": violation_record.violation_type
                }
            )
            stored_files["image"] = image_metadata
            violation_record.image_path = image_metadata.file_path
            
            # Store video segment if provided
            if video_segment:
                video_metadata = await self.store_video_segment(
                    video_segment,
                    f"violation_{violation_record.violation_id}_video",
                    duration_seconds=10.0  # Assuming 10 second segments
                )
                stored_files["video"] = video_metadata
                violation_record.video_segment_path = video_metadata.file_path
            
            # Store violation metadata
            violation_data = {
                "violation_record": violation_record.__dict__,
                "storage_metadata": {k: v.__dict__ for k, v in stored_files.items()},
                "timestamp": datetime.now().isoformat()
            }
            
            metadata_file_id = f"violation_{violation_record.violation_id}_metadata"
            metadata_storage = await self.store_metadata(violation_data, metadata_file_id)
            stored_files["metadata"] = metadata_storage
            
            # Store in database
            db_record_id = self.db_manager.store_violation_record(violation_record)
            
            # Update statistics
            self.storage_stats["files_stored"] += len(stored_files)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Stored violation evidence {violation_record.violation_id} in {processing_time:.2f}ms")
            
            return stored_files
            
        except Exception as e:
            logger.error(f"Failed to store violation evidence {violation_record.violation_id}: {e}")
            self.storage_stats["errors"] += 1
            raise
    
    async def store_image(self, image: np.ndarray, file_id: str,
                         metadata: Optional[Dict] = None) -> StorageMetadata:
        """Store image with intelligent storage placement."""
        start_time = time.time()
        
        try:
            # Calculate image hash for duplicate detection
            image_hash = self._calculate_image_hash(image)
            
            # Check cache for duplicate detection results
            cached_metadata = self.cache_manager.get_processed_frame(f"image_{image_hash}")
            if cached_metadata:
                logger.debug(f"Found duplicate image for {file_id}")
                self.storage_stats["cache_hits"] += 1
                return StorageMetadata(**cached_metadata)
            
            self.storage_stats["cache_misses"] += 1
            
            # Estimate file size
            encoded_image = cv2.imencode('.jpg', image)[1]
            file_size = len(encoded_image.tobytes())
            
            # Determine storage location
            storage_location = self._get_storage_location(DataType.IMAGE, file_size)
            
            # Store based on location
            if storage_location == StorageType.LOCAL:
                storage_metadata = self.local_manager.store_image(image, file_id, metadata)
            elif storage_location == StorageType.S3 and self.cloud_manager:
                image_bytes = encoded_image.tobytes()
                storage_metadata = await self.cloud_manager.upload_file_async(
                    image_bytes, file_id, DataType.IMAGE, metadata
                )
            else:
                # Fallback to local
                storage_metadata = self.local_manager.store_image(image, file_id, metadata)
            
            # Store metadata in database
            self.db_manager.store_storage_metadata(storage_metadata)
            
            # Cache the metadata
            self.cache_manager.store_processed_frame(
                f"image_{image_hash}",
                storage_metadata.__dict__,
                ttl=3600
            )
            
            processing_time = (time.time() - start_time) * 1000
            self.operation_times["store_image"] = processing_time
            
            logger.debug(f"Stored image {file_id} in {processing_time:.2f}ms")
            return storage_metadata
            
        except Exception as e:
            logger.error(f"Failed to store image {file_id}: {e}")
            self.storage_stats["errors"] += 1
            raise
    
    async def store_video_segment(self, video_data: bytes, file_id: str,
                                 duration_seconds: float) -> StorageMetadata:
        """Store video segment with intelligent placement."""
        start_time = time.time()
        
        try:
            file_size = len(video_data)
            storage_location = self._get_storage_location(DataType.VIDEO, file_size)
            
            # Store based on location
            if storage_location == StorageType.LOCAL:
                storage_metadata = self.local_manager.store_video_segment(
                    video_data, file_id, duration_seconds
                )
            elif storage_location == StorageType.S3 and self.cloud_manager:
                storage_metadata = await self.cloud_manager.upload_file_async(
                    video_data, file_id, DataType.VIDEO,
                    metadata={"duration_seconds": str(duration_seconds)}
                )
            else:
                # Fallback to local
                storage_metadata = self.local_manager.store_video_segment(
                    video_data, file_id, duration_seconds
                )
            
            # Store metadata in database
            self.db_manager.store_storage_metadata(storage_metadata)
            
            processing_time = (time.time() - start_time) * 1000
            self.operation_times["store_video"] = processing_time
            
            logger.debug(f"Stored video segment {file_id} in {processing_time:.2f}ms")
            return storage_metadata
            
        except Exception as e:
            logger.error(f"Failed to store video segment {file_id}: {e}")
            self.storage_stats["errors"] += 1
            raise
    
    async def store_metadata(self, data: Dict[str, Any], file_id: str) -> StorageMetadata:
        """Store metadata with intelligent placement."""
        start_time = time.time()
        
        try:
            # Convert to JSON bytes for size estimation
            json_data = json.dumps(data, default=str)
            file_size = len(json_data.encode())
            
            storage_location = self._get_storage_location(DataType.METADATA, file_size)
            
            # Store based on location
            if storage_location == StorageType.LOCAL:
                storage_metadata = self.local_manager.store_metadata(data, file_id)
            elif storage_location == StorageType.S3 and self.cloud_manager:
                storage_metadata = await self.cloud_manager.upload_file_async(
                    json_data.encode(), file_id, DataType.JSON
                )
            else:
                # Fallback to local
                storage_metadata = self.local_manager.store_metadata(data, file_id)
            
            # Store metadata in database
            self.db_manager.store_storage_metadata(storage_metadata)
            
            processing_time = (time.time() - start_time) * 1000
            self.operation_times["store_metadata"] = processing_time
            
            logger.debug(f"Stored metadata {file_id} in {processing_time:.2f}ms")
            return storage_metadata
            
        except Exception as e:
            logger.error(f"Failed to store metadata {file_id}: {e}")
            self.storage_stats["errors"] += 1
            raise
    
    async def retrieve_file(self, file_id: str) -> Tuple[bytes, StorageMetadata]:
        """Retrieve file from any storage backend."""
        start_time = time.time()
        
        try:
            # Get storage metadata from database
            storage_metadata = self.db_manager.get_storage_metadata(file_id)
            
            if not storage_metadata:
                raise FileNotFoundError(f"No storage metadata found for {file_id}")
            
            # Check cache first
            cache_key = f"file_data_{file_id}"
            cached_data = self.cache_manager.redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"Retrieved {file_id} from cache")
                self.storage_stats["cache_hits"] += 1
                self.storage_stats["files_retrieved"] += 1
                return cached_data, storage_metadata
            
            self.storage_stats["cache_misses"] += 1
            
            # Retrieve from appropriate storage
            if storage_metadata.storage_type == StorageType.LOCAL:
                file_data = self.local_manager.retrieve_file(file_id, storage_metadata)
            elif storage_metadata.storage_type == StorageType.S3 and self.cloud_manager:
                file_data = self.cloud_manager.download_file(storage_metadata)
            else:
                raise ValueError(f"Unsupported storage type: {storage_metadata.storage_type}")
            
            # Cache the data for future access (if not too large)
            if len(file_data) < 1024 * 1024:  # Cache files smaller than 1MB
                self.cache_manager.redis_client.setex(cache_key, 3600, file_data)
            
            processing_time = (time.time() - start_time) * 1000
            self.operation_times["retrieve_file"] = processing_time
            self.storage_stats["files_retrieved"] += 1
            
            logger.debug(f"Retrieved file {file_id} in {processing_time:.2f}ms")
            return file_data, storage_metadata
            
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_id}: {e}")
            self.storage_stats["errors"] += 1
            raise
    
    async def retrieve_image(self, file_id: str) -> Tuple[np.ndarray, StorageMetadata]:
        """Retrieve image and decode to numpy array."""
        file_data, storage_metadata = await self.retrieve_file(file_id)
        
        # Decode image
        nparr = np.frombuffer(file_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError(f"Failed to decode image {file_id}")
        
        return image, storage_metadata
    
    def get_violation_records(self, **kwargs) -> List[Dict[str, Any]]:
        """Retrieve violation records with filters."""
        return self.db_manager.get_violation_records(**kwargs)
    
    def generate_access_url(self, file_id: str, expires_in: int = 3600) -> str:
        """Generate temporary access URL for file."""
        storage_metadata = self.db_manager.get_storage_metadata(file_id)
        
        if not storage_metadata:
            raise FileNotFoundError(f"No storage metadata found for {file_id}")
        
        if storage_metadata.storage_type == StorageType.S3 and self.cloud_manager:
            return self.cloud_manager.generate_presigned_url(storage_metadata, expires_in)
        elif storage_metadata.storage_type == StorageType.LOCAL:
            # For local files, we would need a file server to generate URLs
            # For now, return the file path
            return f"file://{storage_metadata.file_path}"
        else:
            raise ValueError(f"Cannot generate URL for storage type: {storage_metadata.storage_type}")
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics."""
        local_usage = self.local_manager.get_storage_usage()
        
        stats = {
            "local_storage": local_usage,
            "operation_stats": self.storage_stats.copy(),
            "performance_metrics": self.operation_times.copy(),
            "cache_info": {
                "redis_info": self.cache_manager.redis_client.info(),
                "cache_keys": self.cache_manager.redis_client.dbsize()
            }
        }
        
        # Add cloud storage stats if available
        if self.cloud_manager:
            stats["cloud_storage"] = {
                "bucket": self.config.s3_bucket,
                "region": self.config.s3_region
            }
        
        return stats
    
    async def cleanup_expired_data(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean up expired data across all storage backends."""
        cleanup_results = {
            "local_files_deleted": 0,
            "cloud_files_deleted": 0,
            "database_records_cleaned": 0,
            "cache_entries_cleared": 0,
            "errors": []
        }
        
        try:
            # Clean local storage
            if not dry_run:
                deleted_local = self.local_manager.cleanup_expired_files()
                cleanup_results["local_files_deleted"] = sum(deleted_local.values())
            
            # Clean cache
            if not dry_run:
                cache_cleared = self.cache_manager.clear_cache("expired:*")
                cleanup_results["cache_entries_cleared"] = cache_cleared
            
            logger.info(f"Cleanup completed: {cleanup_results}")
            
        except Exception as e:
            error_msg = f"Error during cleanup: {e}"
            logger.error(error_msg)
            cleanup_results["errors"].append(error_msg)
        
        return cleanup_results
    
    async def migrate_to_cloud(self, file_age_days: int = 7, 
                              batch_size: int = 50) -> Dict[str, Any]:
        """Migrate old local files to cloud storage."""
        if not self.cloud_manager:
            raise ValueError("Cloud storage not configured")
        
        migration_results = {
            "files_migrated": 0,
            "files_failed": 0,
            "bytes_migrated": 0,
            "errors": []
        }
        
        cutoff_date = datetime.now() - timedelta(days=file_age_days)
        
        # This would need to be implemented based on file tracking
        # For now, return empty results
        
        return migration_results
    
    async def verify_data_integrity(self) -> Dict[str, Any]:
        """Verify data integrity across all storage backends."""
        integrity_results = {
            "files_checked": 0,
            "checksum_mismatches": 0,
            "missing_files": 0,
            "corrupted_files": 0,
            "errors": []
        }
        
        # This would involve checking all stored files against their checksums
        # For now, return empty results
        
        return integrity_results
    
    async def backup_critical_data(self, backup_location: str) -> Dict[str, Any]:
        """Backup critical system data."""
        backup_results = {
            "violation_records_backed_up": 0,
            "metadata_files_backed_up": 0,
            "backup_size_bytes": 0,
            "backup_location": backup_location,
            "errors": []
        }
        
        # This would involve exporting critical data to backup location
        # For now, return empty results
        
        return backup_results
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            if self.cleanup_task and not self.cleanup_task.done():
                self.cleanup_task.cancel()
            
            if self.sync_task and not self.sync_task.done():
                self.sync_task.cancel()
        except Exception as e:
            logger.error(f"Error during StorageService cleanup: {e}")


class ArchiveManager:
    """Manager for archiving and compressing old data."""
    
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service
    
    async def archive_old_violations(self, days_old: int = 90) -> Dict[str, Any]:
        """Archive old violation records to compressed format."""
        archive_results = {
            "records_archived": 0,
            "compression_ratio": 0.0,
            "archive_files_created": 0,
            "original_size_bytes": 0,
            "compressed_size_bytes": 0
        }
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Get old violation records
        old_records = self.storage_service.get_violation_records(
            end_time=cutoff_date,
            limit=1000
        )
        
        if not old_records:
            return archive_results
        
        # Group records by date for archiving
        records_by_date = {}
        for record in old_records:
            date_key = record['timestamp'].strftime('%Y-%m-%d')
            if date_key not in records_by_date:
                records_by_date[date_key] = []
            records_by_date[date_key].append(record)
        
        # Create compressed archives
        for date_key, date_records in records_by_date.items():
            archive_data = {
                "date": date_key,
                "records": date_records,
                "archived_at": datetime.now().isoformat(),
                "record_count": len(date_records)
            }
            
            archive_id = f"archive_{date_key}_{int(time.time())}"
            
            try:
                # Store as compressed metadata
                await self.storage_service.store_metadata(archive_data, archive_id)
                
                archive_results["records_archived"] += len(date_records)
                archive_results["archive_files_created"] += 1
                
            except Exception as e:
                logger.error(f"Failed to archive records for {date_key}: {e}")
        
        return archive_results