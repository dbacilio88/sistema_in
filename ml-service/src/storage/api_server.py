"""
Storage API server for traffic analysis system.

This module provides REST API endpoints for managing storage operations,
file uploads, downloads, and data management.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import tempfile
import mimetypes

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

import numpy as np
import cv2

from ..storage import (
    StorageService, StorageStrategy, StorageConfig, ViolationRecord,
    DataValidator, DataLifecycleManager, DataAnalyzer, DataExporter
)


logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class ViolationRecordRequest(BaseModel):
    """Request model for violation record creation."""
    violation_id: str
    device_id: str
    violation_type: str
    timestamp: datetime
    vehicle_bbox: List[int]
    license_plate: Optional[str] = None
    vehicle_class: str
    confidence: float
    speed_kmh: Optional[float] = None
    speed_limit: Optional[float] = None
    trajectory: Optional[List[Dict[str, Any]]] = None
    camera_info: Optional[Dict[str, Any]] = None
    processing_time_ms: float
    model_versions: Optional[Dict[str, str]] = None
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v
    
    @validator('vehicle_bbox')
    def validate_bbox(cls, v):
        if len(v) != 4:
            raise ValueError('Bounding box must have 4 coordinates')
        x1, y1, x2, y2 = v
        if x1 >= x2 or y1 >= y2:
            raise ValueError('Invalid bounding box coordinates')
        return v


class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    file_id: str
    storage_type: str
    file_size: int
    checksum: str
    created_at: datetime
    access_url: Optional[str] = None


class StorageStatsResponse(BaseModel):
    """Response model for storage statistics."""
    local_storage: Dict[str, Any]
    operation_stats: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    cache_info: Dict[str, Any]


class ViolationQueryParams(BaseModel):
    """Query parameters for violation search."""
    device_id: Optional[str] = None
    violation_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    
    @validator('limit')
    def validate_limit(cls, v):
        if not 1 <= v <= 10000:
            raise ValueError('Limit must be between 1 and 10000')
        return v


class CleanupRequest(BaseModel):
    """Request model for data cleanup operations."""
    dry_run: bool = True
    max_age_days: int = 90
    
    @validator('max_age_days')
    def validate_max_age(cls, v):
        if v < 1:
            raise ValueError('Max age must be at least 1 day')
        return v


class ExportRequest(BaseModel):
    """Request model for data export."""
    format: str  # 'csv', 'json'
    start_date: datetime
    end_date: datetime
    include_files: bool = False
    
    @validator('format')
    def validate_format(cls, v):
        if v not in ['csv', 'json']:
            raise ValueError('Format must be csv or json')
        return v


def create_storage_app(storage_config: StorageConfig = None) -> FastAPI:
    """Create FastAPI application for storage management."""
    
    app = FastAPI(
        title="Traffic Analysis Storage API",
        description="REST API for managing traffic analysis data storage",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize storage service
    if storage_config is None:
        storage_config = StorageConfig()
    
    storage_service = StorageService(storage_config, StorageStrategy.HYBRID)
    validator = DataValidator()
    lifecycle_manager = DataLifecycleManager(storage_service)
    analyzer = DataAnalyzer(storage_service)
    exporter = DataExporter(storage_service)
    
    @app.on_event("startup")
    async def startup_event():
        """Application startup tasks."""
        logger.info("Starting Storage API server")
        logger.info(f"Storage strategy: {storage_service.strategy}")
        logger.info(f"Local storage path: {storage_config.local_base_path}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown tasks."""
        logger.info("Shutting down Storage API server")
        # Cleanup resources if needed
    
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "service": "Traffic Analysis Storage API",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            # Check storage service health
            stats = storage_service.get_storage_statistics()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "storage_available": True,
                "local_usage_percent": stats.get("local_storage", {}).get("usage_percentage", 0)
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Service unhealthy"
            )
    
    @app.post("/files/upload/image", response_model=FileUploadResponse)
    async def upload_image(
        file: UploadFile = File(...),
        file_id: Optional[str] = Query(None),
        device_id: Optional[str] = Query(None),
        violation_id: Optional[str] = Query(None)
    ):
        """Upload image file."""
        try:
            # Generate file ID if not provided
            if not file_id:
                file_id = f"img_{int(datetime.now().timestamp())}_{file.filename}"
            
            # Validate file type
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="File must be an image"
                )
            
            # Read and decode image
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid image file"
                )
            
            # Validate image
            validation_result = validator._validate_image_data(image)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f"Image validation failed: {validation_result['errors']}"
                )
            
            # Prepare metadata
            metadata = {
                "original_filename": file.filename,
                "content_type": file.content_type,
                "upload_timestamp": datetime.now().isoformat()
            }
            
            if device_id:
                metadata["device_id"] = device_id
            if violation_id:
                metadata["violation_id"] = violation_id
            
            # Store image
            storage_metadata = await storage_service.store_image(image, file_id, metadata)
            
            # Generate access URL
            try:
                access_url = storage_service.generate_access_url(file_id)
            except Exception:
                access_url = None
            
            return FileUploadResponse(
                file_id=storage_metadata.id,
                storage_type=storage_metadata.storage_type.value,
                file_size=storage_metadata.file_size,
                checksum=storage_metadata.checksum,
                created_at=storage_metadata.created_at,
                access_url=access_url
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image"
            )
    
    @app.post("/files/upload/video", response_model=FileUploadResponse)
    async def upload_video(
        file: UploadFile = File(...),
        file_id: Optional[str] = Query(None),
        duration_seconds: Optional[float] = Query(None)
    ):
        """Upload video file."""
        try:
            # Generate file ID if not provided
            if not file_id:
                file_id = f"vid_{int(datetime.now().timestamp())}_{file.filename}"
            
            # Validate file type
            if not file.content_type.startswith('video/'):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="File must be a video"
                )
            
            # Read video data
            video_data = await file.read()
            
            # Validate video
            validation_result = validator._validate_video_data(video_data)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f"Video validation failed: {validation_result['errors']}"
                )
            
            # Store video
            storage_metadata = await storage_service.store_video_segment(
                video_data, 
                file_id, 
                duration_seconds or 10.0
            )
            
            # Generate access URL
            try:
                access_url = storage_service.generate_access_url(file_id)
            except Exception:
                access_url = None
            
            return FileUploadResponse(
                file_id=storage_metadata.id,
                storage_type=storage_metadata.storage_type.value,
                file_size=storage_metadata.file_size,
                checksum=storage_metadata.checksum,
                created_at=storage_metadata.created_at,
                access_url=access_url
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload video"
            )
    
    @app.get("/files/{file_id}")
    async def download_file(file_id: str):
        """Download file by ID."""
        try:
            file_data, storage_metadata = await storage_service.retrieve_file(file_id)
            
            # Determine content type
            if storage_metadata.data_type.value == "image":
                content_type = "image/jpeg"
                filename = f"{file_id}.jpg"
            elif storage_metadata.data_type.value == "video":
                content_type = "video/mp4"
                filename = f"{file_id}.mp4"
            elif storage_metadata.data_type.value == "metadata":
                content_type = "application/json"
                filename = f"{file_id}.json"
            else:
                content_type = "application/octet-stream"
                filename = file_id
            
            return StreamingResponse(
                io.BytesIO(file_data),
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        except FileNotFoundError:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download file"
            )
    
    @app.get("/files/{file_id}/url")
    async def get_file_url(file_id: str, expires_in: int = Query(3600)):
        """Get temporary access URL for file."""
        try:
            url = storage_service.generate_access_url(file_id, expires_in)
            return {
                "file_id": file_id,
                "access_url": url,
                "expires_in": expires_in,
                "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
            }
            
        except FileNotFoundError:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        except Exception as e:
            logger.error(f"Error generating URL for {file_id}: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access URL"
            )
    
    @app.post("/violations", response_model=Dict[str, str])
    async def create_violation_record(
        violation: ViolationRecordRequest,
        image_file: Optional[UploadFile] = File(None),
        video_file: Optional[UploadFile] = File(None)
    ):
        """Create violation record with evidence files."""
        try:
            # Convert request to ViolationRecord
            violation_record = ViolationRecord(
                violation_id=violation.violation_id,
                device_id=violation.device_id,
                violation_type=violation.violation_type,
                timestamp=violation.timestamp,
                vehicle_bbox=violation.vehicle_bbox,
                license_plate=violation.license_plate,
                vehicle_class=violation.vehicle_class,
                confidence=violation.confidence,
                speed_kmh=violation.speed_kmh,
                speed_limit=violation.speed_limit,
                trajectory=violation.trajectory or [],
                image_path="",  # Will be set by storage service
                video_segment_path=None,
                camera_info=violation.camera_info or {},
                processing_time_ms=violation.processing_time_ms,
                model_versions=violation.model_versions or {}
            )
            
            # Validate violation record
            validation_result = validator.validate_violation_record(violation_record)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f"Violation record validation failed: {validation_result['errors']}"
                )
            
            # Process evidence files
            image = None
            video_data = None
            
            if image_file:
                contents = await image_file.read()
                nparr = np.frombuffer(contents, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail="Invalid image file"
                    )
            
            if video_file:
                video_data = await video_file.read()
            
            # Store violation evidence
            stored_files = await storage_service.store_violation_evidence(
                violation_record, image, video_data
            )
            
            return {
                "violation_id": violation_record.violation_id,
                "status": "created",
                "files_stored": list(stored_files.keys()),
                "validation_score": validation_result["score"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating violation record: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create violation record"
            )
    
    @app.get("/violations")
    async def get_violations(
        device_id: Optional[str] = Query(None),
        violation_type: Optional[str] = Query(None),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        limit: int = Query(100)
    ):
        """Get violation records with filters."""
        try:
            # Validate parameters
            params = ViolationQueryParams(
                device_id=device_id,
                violation_type=violation_type,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            # Get violation records
            violations = storage_service.get_violation_records(
                device_id=params.device_id,
                violation_type=params.violation_type,
                start_time=params.start_date,
                end_time=params.end_date,
                limit=params.limit
            )
            
            return {
                "total": len(violations),
                "violations": violations,
                "query_parameters": params.dict(exclude_none=True)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving violations: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve violations"
            )
    
    @app.get("/storage/stats", response_model=StorageStatsResponse)
    async def get_storage_statistics():
        """Get storage statistics."""
        try:
            stats = storage_service.get_storage_statistics()
            return StorageStatsResponse(**stats)
            
        except Exception as e:
            logger.error(f"Error getting storage statistics: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get storage statistics"
            )
    
    @app.post("/storage/cleanup")
    async def cleanup_storage(
        request: CleanupRequest,
        background_tasks: BackgroundTasks
    ):
        """Clean up expired data."""
        try:
            if request.dry_run:
                # Simulate cleanup without actually deleting
                result = await storage_service.cleanup_expired_data(dry_run=True)
            else:
                # Run actual cleanup in background
                background_tasks.add_task(
                    storage_service.cleanup_expired_data,
                    dry_run=False
                )
                result = {"status": "cleanup_started", "dry_run": False}
            
            return result
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cleanup storage"
            )
    
    @app.post("/data/export")
    async def export_data(request: ExportRequest, background_tasks: BackgroundTasks):
        """Export violation data."""
        try:
            # Generate unique export ID
            export_id = f"export_{int(datetime.now().timestamp())}"
            
            if request.format == "csv":
                output_path = f"/tmp/{export_id}.csv"
                background_tasks.add_task(
                    exporter.export_violations_csv,
                    request.start_date,
                    request.end_date,
                    output_path
                )
            elif request.format == "json":
                output_path = f"/tmp/{export_id}.json"
                background_tasks.add_task(
                    exporter.export_statistics_json,
                    output_path
                )
            
            return {
                "export_id": export_id,
                "status": "started",
                "format": request.format,
                "output_path": output_path
            }
            
        except Exception as e:
            logger.error(f"Error starting export: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start export"
            )
    
    @app.get("/analytics/quality")
    async def get_data_quality_analysis(sample_size: int = Query(1000)):
        """Get data quality analysis."""
        try:
            analysis = await analyzer.analyze_data_quality(sample_size)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing data quality: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to analyze data quality"
            )
    
    @app.get("/analytics/storage")
    async def get_storage_analysis():
        """Get storage usage analysis."""
        try:
            analysis = await analyzer.analyze_storage_patterns()
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing storage patterns: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to analyze storage patterns"
            )
    
    @app.post("/lifecycle/snapshot")
    async def create_data_snapshot(snapshot_id: str):
        """Create data snapshot."""
        try:
            result = await lifecycle_manager.create_data_snapshot(snapshot_id)
            return result
            
        except Exception as e:
            logger.error(f"Error creating snapshot: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create snapshot"
            )
    
    @app.post("/lifecycle/retention")
    async def apply_retention_policies(background_tasks: BackgroundTasks):
        """Apply data retention policies."""
        try:
            background_tasks.add_task(lifecycle_manager.apply_retention_policies)
            
            return {
                "status": "retention_policies_started",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error applying retention policies: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to apply retention policies"
            )
    
    return app


# Import required modules at module level
import io


def main():
    """Main function to run the storage API server."""
    import uvicorn
    
    # Create default configuration
    config = StorageConfig()
    
    # Create FastAPI app
    app = create_storage_app(config)
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False
    )


if __name__ == "__main__":
    main()