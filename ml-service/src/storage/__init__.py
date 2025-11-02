"""
Storage module initialization.

This module provides comprehensive data storage and management capabilities
for the traffic analysis system.
"""

from .storage_manager import (
    StorageConfig,
    StorageType,
    DataType,
    StorageMetadata,
    ViolationRecord,
    LocalStorageManager,
    CloudStorageManager,
    DatabaseManager,
    CacheManager
)

from .storage_service import (
    StorageService,
    StorageStrategy,
    ArchiveManager
)

from .data_utils import (
    DataValidator,
    DataLifecycleManager,
    DataMigrationManager,
    DataAnalyzer,
    DataExporter
)

__all__ = [
    # Storage configuration and types
    'StorageConfig',
    'StorageType',
    'DataType',
    'StorageMetadata',
    'ViolationRecord',
    
    # Storage managers
    'LocalStorageManager',
    'CloudStorageManager',
    'DatabaseManager',
    'CacheManager',
    
    # High-level services
    'StorageService',
    'StorageStrategy',
    'ArchiveManager',
    
    # Data utilities
    'DataValidator',
    'DataLifecycleManager',
    'DataMigrationManager',
    'DataAnalyzer',
    'DataExporter'
]

# Version information
__version__ = "1.0.0"
__author__ = "Traffic Analysis System Team"