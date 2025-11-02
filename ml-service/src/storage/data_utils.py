"""
Data management utilities for traffic analysis system.

This module provides utilities for data lifecycle management,
data quality validation, and data migration tasks.
"""

import os
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Generator, Tuple
from pathlib import Path
import json
import csv
import hashlib
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import asdict
import statistics

import numpy as np
import cv2
from PIL import Image
import pandas as pd

from .storage_service import StorageService, StorageStrategy
from .storage_manager import StorageConfig, ViolationRecord, StorageMetadata, DataType


logger = logging.getLogger(__name__)


class DataValidator:
    """Data validation utilities for ensuring data quality."""
    
    def __init__(self):
        self.validation_rules = {
            'violation_record': self._validate_violation_record,
            'image_data': self._validate_image_data,
            'video_data': self._validate_video_data,
            'metadata': self._validate_metadata
        }
    
    def validate_violation_record(self, record: ViolationRecord) -> Dict[str, Any]:
        """Validate violation record completeness and accuracy."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 1.0
        }
        
        # Required fields validation
        required_fields = [
            'violation_id', 'device_id', 'violation_type', 'timestamp',
            'vehicle_bbox', 'vehicle_class', 'confidence', 'image_path'
        ]
        
        for field in required_fields:
            if not hasattr(record, field) or getattr(record, field) is None:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["valid"] = False
        
        # Data quality checks
        if hasattr(record, 'confidence') and record.confidence is not None:
            if not 0.0 <= record.confidence <= 1.0:
                validation_result["errors"].append("Confidence must be between 0.0 and 1.0")
                validation_result["valid"] = False
            elif record.confidence < 0.5:
                validation_result["warnings"].append("Low confidence detection")
        
        # Bounding box validation
        if hasattr(record, 'vehicle_bbox') and record.vehicle_bbox:
            if len(record.vehicle_bbox) != 4:
                validation_result["errors"].append("Vehicle bbox must have 4 coordinates")
                validation_result["valid"] = False
            else:
                x1, y1, x2, y2 = record.vehicle_bbox
                if x1 >= x2 or y1 >= y2:
                    validation_result["errors"].append("Invalid bounding box coordinates")
                    validation_result["valid"] = False
        
        # Speed validation
        if hasattr(record, 'speed_kmh') and record.speed_kmh is not None:
            if record.speed_kmh < 0 or record.speed_kmh > 300:  # Reasonable speed limits
                validation_result["errors"].append("Speed value out of reasonable range")
                validation_result["valid"] = False
        
        # License plate validation
        if hasattr(record, 'license_plate') and record.license_plate:
            # Basic Peruvian license plate format validation
            if not self._validate_license_plate_format(record.license_plate):
                validation_result["warnings"].append("License plate format may be invalid")
        
        # Calculate validation score
        error_weight = 0.3
        warning_weight = 0.1
        score = 1.0 - (len(validation_result["errors"]) * error_weight + 
                      len(validation_result["warnings"]) * warning_weight)
        validation_result["score"] = max(0.0, score)
        
        return validation_result
    
    def _validate_license_plate_format(self, plate: str) -> bool:
        """Validate Peruvian license plate format."""
        import re
        
        # Peruvian license plate patterns
        patterns = [
            r'^[A-Z]{3}-\d{3}$',      # AAA-123 (old format)
            r'^[A-Z]{3}\d{3}$',       # AAA123 (old format without dash)
            r'^[A-Z]{3}-\d{4}$',      # AAA-1234 (new format)
            r'^[A-Z]{3}\d{4}$',       # AAA1234 (new format without dash)
        ]
        
        return any(re.match(pattern, plate.upper()) for pattern in patterns)
    
    def _validate_image_data(self, image: np.ndarray) -> Dict[str, Any]:
        """Validate image data quality."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        if image is None:
            validation_result["errors"].append("Image is None")
            validation_result["valid"] = False
            return validation_result
        
        # Basic image properties
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        validation_result["metrics"] = {
            "width": width,
            "height": height,
            "channels": channels,
            "size_bytes": image.nbytes
        }
        
        # Minimum resolution check
        if width < 640 or height < 480:
            validation_result["warnings"].append("Low resolution image")
        
        # Maximum resolution check
        if width > 4096 or height > 4096:
            validation_result["warnings"].append("Very high resolution image")
        
        # Brightness analysis
        if channels >= 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        mean_brightness = np.mean(gray)
        validation_result["metrics"]["mean_brightness"] = mean_brightness
        
        if mean_brightness < 50:
            validation_result["warnings"].append("Image appears too dark")
        elif mean_brightness > 200:
            validation_result["warnings"].append("Image appears too bright")
        
        # Blur detection using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        validation_result["metrics"]["blur_score"] = laplacian_var
        
        if laplacian_var < 100:
            validation_result["warnings"].append("Image appears blurry")
        
        return validation_result
    
    def _validate_video_data(self, video_data: bytes) -> Dict[str, Any]:
        """Validate video data quality."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        if not video_data:
            validation_result["errors"].append("Video data is empty")
            validation_result["valid"] = False
            return validation_result
        
        validation_result["metrics"]["size_bytes"] = len(video_data)
        
        # Check minimum size (videos should be larger than images)
        if len(video_data) < 1024:  # 1KB minimum
            validation_result["errors"].append("Video file too small")
            validation_result["valid"] = False
        
        # Check maximum size (reasonable limit for video segments)
        if len(video_data) > 100 * 1024 * 1024:  # 100MB maximum
            validation_result["warnings"].append("Video file very large")
        
        return validation_result
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata completeness."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        if not metadata:
            validation_result["errors"].append("Metadata is empty")
            validation_result["valid"] = False
            return validation_result
        
        # Check for critical metadata fields
        critical_fields = ['timestamp', 'device_id', 'processing_info']
        for field in critical_fields:
            if field not in metadata:
                validation_result["warnings"].append(f"Missing metadata field: {field}")
        
        validation_result["metrics"]["field_count"] = len(metadata)
        
        return validation_result


class DataLifecycleManager:
    """Manager for data lifecycle operations including retention and archival."""
    
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service
        self.retention_policies = {
            "violation_images": timedelta(days=90),
            "violation_videos": timedelta(days=30),
            "violation_metadata": timedelta(days=365),
            "debug_data": timedelta(days=7),
            "cache_data": timedelta(hours=24)
        }
    
    async def apply_retention_policies(self) -> Dict[str, Any]:
        """Apply data retention policies across all data types."""
        retention_results = {
            "policies_applied": 0,
            "files_deleted": 0,
            "space_freed_bytes": 0,
            "errors": []
        }
        
        current_time = datetime.now()
        
        for policy_name, retention_period in self.retention_policies.items():
            try:
                cutoff_time = current_time - retention_period
                
                # Get files older than retention period
                # This would need to be implemented based on metadata tracking
                deleted_count = await self._delete_old_files(policy_name, cutoff_time)
                
                retention_results["files_deleted"] += deleted_count
                retention_results["policies_applied"] += 1
                
                logger.info(f"Applied retention policy {policy_name}: {deleted_count} files deleted")
                
            except Exception as e:
                error_msg = f"Error applying retention policy {policy_name}: {e}"
                logger.error(error_msg)
                retention_results["errors"].append(error_msg)
        
        return retention_results
    
    async def _delete_old_files(self, policy_name: str, cutoff_time: datetime) -> int:
        """Delete files older than cutoff time for a specific policy."""
        # This would need to query the database for files matching the policy
        # For now, return 0
        return 0
    
    async def create_data_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Create a point-in-time snapshot of critical data."""
        snapshot_results = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
            "violation_records_count": 0,
            "storage_metadata_count": 0,
            "snapshot_size_bytes": 0,
            "snapshot_location": ""
        }
        
        # Get current violation records
        recent_violations = self.storage_service.get_violation_records(
            start_time=datetime.now() - timedelta(days=1),
            limit=10000
        )
        
        snapshot_data = {
            "metadata": snapshot_results,
            "violation_records": recent_violations,
            "system_state": await self._capture_system_state()
        }
        
        # Store snapshot
        snapshot_file_id = f"snapshot_{snapshot_id}_{int(time.time())}"
        storage_metadata = await self.storage_service.store_metadata(
            snapshot_data, 
            snapshot_file_id
        )
        
        snapshot_results["violation_records_count"] = len(recent_violations)
        snapshot_results["snapshot_size_bytes"] = storage_metadata.file_size
        snapshot_results["snapshot_location"] = storage_metadata.file_path
        
        return snapshot_results
    
    async def _capture_system_state(self) -> Dict[str, Any]:
        """Capture current system state for snapshot."""
        return {
            "storage_statistics": self.storage_service.get_storage_statistics(),
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "retention_policies": {
                    name: str(period) for name, period in self.retention_policies.items()
                }
            }
        }


class DataMigrationManager:
    """Manager for data migration between storage systems."""
    
    def __init__(self, source_storage: StorageService, target_storage: StorageService):
        self.source_storage = source_storage
        self.target_storage = target_storage
        self.migration_batch_size = 100
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def migrate_violation_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Migrate violation data between storage systems."""
        migration_results = {
            "total_records": 0,
            "migrated_records": 0,
            "failed_records": 0,
            "migrated_files": 0,
            "failed_files": 0,
            "total_size_bytes": 0,
            "errors": []
        }
        
        # Get violation records in date range
        violation_records = self.source_storage.get_violation_records(
            start_time=start_date,
            end_time=end_date,
            limit=10000
        )
        
        migration_results["total_records"] = len(violation_records)
        
        # Process in batches
        for i in range(0, len(violation_records), self.migration_batch_size):
            batch = violation_records[i:i + self.migration_batch_size]
            
            try:
                batch_results = await self._migrate_record_batch(batch)
                
                migration_results["migrated_records"] += batch_results["migrated_records"]
                migration_results["failed_records"] += batch_results["failed_records"]
                migration_results["migrated_files"] += batch_results["migrated_files"]
                migration_results["failed_files"] += batch_results["failed_files"]
                migration_results["total_size_bytes"] += batch_results["total_size_bytes"]
                
                if batch_results["errors"]:
                    migration_results["errors"].extend(batch_results["errors"])
                
                logger.info(f"Migrated batch {i//self.migration_batch_size + 1}: "
                           f"{batch_results['migrated_records']} records")
                
            except Exception as e:
                error_msg = f"Error migrating batch {i//self.migration_batch_size + 1}: {e}"
                logger.error(error_msg)
                migration_results["errors"].append(error_msg)
                migration_results["failed_records"] += len(batch)
        
        return migration_results
    
    async def _migrate_record_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Migrate a batch of violation records."""
        batch_results = {
            "migrated_records": 0,
            "failed_records": 0,
            "migrated_files": 0,
            "failed_files": 0,
            "total_size_bytes": 0,
            "errors": []
        }
        
        for record in records:
            try:
                # Migrate associated files
                files_migrated = await self._migrate_record_files(record)
                
                batch_results["migrated_files"] += files_migrated["migrated_count"]
                batch_results["failed_files"] += files_migrated["failed_count"]
                batch_results["total_size_bytes"] += files_migrated["total_size"]
                
                if files_migrated["errors"]:
                    batch_results["errors"].extend(files_migrated["errors"])
                
                # If files migrated successfully, record is considered migrated
                if files_migrated["failed_count"] == 0:
                    batch_results["migrated_records"] += 1
                else:
                    batch_results["failed_records"] += 1
                
            except Exception as e:
                error_msg = f"Error migrating record {record.get('violation_id', 'unknown')}: {e}"
                logger.error(error_msg)
                batch_results["errors"].append(error_msg)
                batch_results["failed_records"] += 1
        
        return batch_results
    
    async def _migrate_record_files(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate files associated with a violation record."""
        file_results = {
            "migrated_count": 0,
            "failed_count": 0,
            "total_size": 0,
            "errors": []
        }
        
        # List of file paths to migrate
        file_paths = []
        if record.get('image_path'):
            file_paths.append(record['image_path'])
        if record.get('video_segment_path'):
            file_paths.append(record['video_segment_path'])
        
        for file_path in file_paths:
            try:
                # Extract file ID from path (this would need proper implementation)
                file_id = Path(file_path).stem
                
                # Retrieve from source
                file_data, metadata = await self.source_storage.retrieve_file(file_id)
                
                # Store in target
                if metadata.data_type == DataType.IMAGE:
                    # Decode and re-encode image
                    nparr = np.frombuffer(file_data, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    await self.target_storage.store_image(image, file_id)
                else:
                    # Store raw data
                    await self.target_storage.store_metadata(
                        {"data": file_data.hex()}, 
                        file_id
                    )
                
                file_results["migrated_count"] += 1
                file_results["total_size"] += len(file_data)
                
            except Exception as e:
                error_msg = f"Error migrating file {file_path}: {e}"
                logger.error(error_msg)
                file_results["errors"].append(error_msg)
                file_results["failed_count"] += 1
        
        return file_results


class DataAnalyzer:
    """Analyzer for data quality and usage patterns."""
    
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service
        self.validator = DataValidator()
    
    async def analyze_data_quality(self, sample_size: int = 1000) -> Dict[str, Any]:
        """Analyze data quality across stored violation records."""
        quality_results = {
            "total_analyzed": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "average_quality_score": 0.0,
            "common_errors": {},
            "quality_distribution": {},
            "recommendations": []
        }
        
        # Get recent violation records
        recent_violations = self.storage_service.get_violation_records(
            start_time=datetime.now() - timedelta(days=7),
            limit=sample_size
        )
        
        quality_scores = []
        error_counts = {}
        
        for record_data in recent_violations:
            try:
                # Convert dict to ViolationRecord for validation
                # This would need proper conversion implementation
                
                # For now, simulate validation
                validation_result = {
                    "valid": True,
                    "errors": [],
                    "warnings": [],
                    "score": 0.8 + (hash(str(record_data)) % 20) / 100  # Simulated score
                }
                
                quality_scores.append(validation_result["score"])
                
                if validation_result["valid"]:
                    quality_results["valid_records"] += 1
                else:
                    quality_results["invalid_records"] += 1
                
                # Count error types
                for error in validation_result["errors"]:
                    error_type = error.split(":")[0] if ":" in error else error
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
                
            except Exception as e:
                logger.error(f"Error analyzing record: {e}")
                quality_results["invalid_records"] += 1
        
        quality_results["total_analyzed"] = len(recent_violations)
        quality_results["average_quality_score"] = statistics.mean(quality_scores) if quality_scores else 0.0
        quality_results["common_errors"] = dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Create quality distribution
        if quality_scores:
            quality_results["quality_distribution"] = {
                "excellent (>0.9)": len([s for s in quality_scores if s > 0.9]),
                "good (0.7-0.9)": len([s for s in quality_scores if 0.7 <= s <= 0.9]),
                "fair (0.5-0.7)": len([s for s in quality_scores if 0.5 <= s < 0.7]),
                "poor (<0.5)": len([s for s in quality_scores if s < 0.5])
            }
        
        # Generate recommendations
        quality_results["recommendations"] = self._generate_quality_recommendations(quality_results)
        
        return quality_results
    
    def _generate_quality_recommendations(self, quality_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on quality analysis."""
        recommendations = []
        
        avg_score = quality_results.get("average_quality_score", 0.0)
        
        if avg_score < 0.7:
            recommendations.append("Consider improving detection model accuracy or confidence thresholds")
        
        if quality_results.get("invalid_records", 0) > quality_results.get("total_analyzed", 1) * 0.1:
            recommendations.append("High number of invalid records - review data validation pipeline")
        
        common_errors = quality_results.get("common_errors", {})
        if "Low confidence detection" in common_errors:
            recommendations.append("Consider adjusting detection confidence thresholds")
        
        if "Missing required field" in common_errors:
            recommendations.append("Review data collection pipeline for completeness")
        
        return recommendations
    
    async def analyze_storage_patterns(self) -> Dict[str, Any]:
        """Analyze storage usage patterns and trends."""
        storage_stats = self.storage_service.get_storage_statistics()
        
        pattern_analysis = {
            "storage_efficiency": self._calculate_storage_efficiency(storage_stats),
            "growth_trends": await self._analyze_growth_trends(),
            "access_patterns": await self._analyze_access_patterns(),
            "cost_optimization": self._analyze_cost_optimization(storage_stats)
        }
        
        return pattern_analysis
    
    def _calculate_storage_efficiency(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate storage efficiency metrics."""
        local_stats = stats.get("local_storage", {})
        
        return {
            "utilization_percentage": local_stats.get("usage_percentage", 0),
            "compression_ratio": 0.65,  # Simulated compression ratio
            "deduplication_savings": 0.15  # Simulated deduplication savings
        }
    
    async def _analyze_growth_trends(self) -> Dict[str, Any]:
        """Analyze data growth trends."""
        # This would analyze historical data to predict growth
        return {
            "daily_growth_mb": 1024,  # Simulated daily growth
            "weekly_growth_gb": 7.5,
            "projected_monthly_gb": 30,
            "trend": "increasing"
        }
    
    async def _analyze_access_patterns(self) -> Dict[str, Any]:
        """Analyze data access patterns."""
        # This would analyze access logs to understand usage patterns
        return {
            "hot_data_percentage": 20,  # Data accessed in last 7 days
            "warm_data_percentage": 30,  # Data accessed in last 30 days
            "cold_data_percentage": 50,  # Data not accessed in 30+ days
            "peak_access_hours": [8, 9, 10, 17, 18, 19]  # Hours with highest access
        }
    
    def _analyze_cost_optimization(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost optimization opportunities."""
        return {
            "cold_storage_candidates_gb": 15.5,  # Data that could move to cheaper storage
            "compression_potential_gb": 8.2,     # Additional compression possible
            "cleanup_potential_gb": 3.1,         # Data that could be deleted
            "estimated_monthly_savings_usd": 45.0
        }


class DataExporter:
    """Utilities for exporting data in various formats."""
    
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service
    
    async def export_violations_csv(self, start_date: datetime, end_date: datetime,
                                   output_path: str) -> Dict[str, Any]:
        """Export violation records to CSV format."""
        export_results = {
            "records_exported": 0,
            "file_size_bytes": 0,
            "output_path": output_path,
            "columns": []
        }
        
        # Get violation records
        violations = self.storage_service.get_violation_records(
            start_time=start_date,
            end_time=end_date,
            limit=100000
        )
        
        if not violations:
            export_results["records_exported"] = 0
            return export_results
        
        # Convert to DataFrame for easy CSV export
        df = pd.DataFrame(violations)
        
        # Export to CSV
        df.to_csv(output_path, index=False)
        
        export_results["records_exported"] = len(violations)
        export_results["file_size_bytes"] = os.path.getsize(output_path)
        export_results["columns"] = list(df.columns)
        
        logger.info(f"Exported {len(violations)} violation records to {output_path}")
        
        return export_results
    
    async def export_statistics_json(self, output_path: str) -> Dict[str, Any]:
        """Export system statistics to JSON format."""
        stats = self.storage_service.get_storage_statistics()
        
        # Add analysis data
        stats["export_timestamp"] = datetime.now().isoformat()
        stats["data_quality"] = await DataAnalyzer(self.storage_service).analyze_data_quality(100)
        
        # Export to JSON
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        return {
            "file_size_bytes": os.path.getsize(output_path),
            "output_path": output_path,
            "sections_exported": list(stats.keys())
        }