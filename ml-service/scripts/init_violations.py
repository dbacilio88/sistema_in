#!/usr/bin/env python3
"""
Initialization script for the traffic violations detection system.

This script sets up the violation detection environment, initializes databases,
configures notification channels, and validates the system setup.
"""

import os
import sys
import sqlite3
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directories to path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

from src.violations.violation_detector import ViolationDetector, ViolationType, ViolationSeverity
from src.violations.lane_detector import LaneDetector
from src.violations.notification_system import NotificationSystem, NotificationChannel, NotificationConfig
from src.violations.violation_manager import ViolationManager


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('violations_init.log')
        ]
    )


def create_directory_structure(base_dir: Path) -> None:
    """Create necessary directory structure."""
    logger = logging.getLogger(__name__)
    
    directories = [
        base_dir / "data" / "violations",
        base_dir / "data" / "reports", 
        base_dir / "data" / "evidence",
        base_dir / "data" / "notifications",
        base_dir / "logs",
        base_dir / "config"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def initialize_violation_database(db_path: Path) -> bool:
    """Initialize the violations database."""
    logger = logging.getLogger(__name__)
    
    try:
        # Create ViolationManager to initialize database
        manager = ViolationManager()
        manager.db_path = str(db_path)
        manager._init_database()
        
        logger.info(f"Initialized violations database: {db_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


def create_default_config(config_path: Path) -> Dict[str, Any]:
    """Create default configuration file."""
    logger = logging.getLogger(__name__)
    
    default_config = {
        "violation_detection": {
            "speed_threshold_minor": 10.0,
            "speed_threshold_moderate": 20.0,
            "speed_threshold_severe": 40.0,
            "speed_threshold_critical": 60.0,
            "following_distance_min": 15.0,
            "wrong_way_angle_threshold": 90.0,
            "lane_violation_threshold": 0.3,
            "confidence_threshold": 0.7,
            "cooldown_periods": {
                "speed_violation": 30.0,
                "lane_violation": 15.0,
                "wrong_way": 60.0,
                "following_distance": 20.0
            }
        },
        "lane_detection": {
            "image_width": 1920,
            "image_height": 1080,
            "roi_height_ratio": 0.6,
            "roi_width_ratio": 0.8,
            "canny_low_threshold": 50,
            "canny_high_threshold": 150,
            "hough_threshold": 50,
            "hough_min_line_length": 100,
            "hough_max_line_gap": 50,
            "polynomial_degree": 2,
            "smoothing_factor": 0.7
        },
        "notifications": {
            "enabled_channels": ["database", "file"],
            "rate_limits": {
                "email": 10,
                "sms": 5,
                "webhook": 100,
                "database": 1000,
                "file": 500
            },
            "priority_thresholds": {
                "critical": ["wrong_way", "severe_speed"],
                "high": ["moderate_speed", "lane_violation"],
                "medium": ["minor_speed", "following_distance"],
                "low": ["info"]
            }
        },
        "evidence": {
            "save_evidence": True,
            "evidence_formats": ["image", "video"],
            "retention_days": 30,
            "max_evidence_size_mb": 100
        },
        "reporting": {
            "auto_reports": True,
            "report_intervals": ["hourly", "daily", "weekly"],
            "report_formats": ["json", "csv"],
            "include_statistics": True
        },
        "system": {
            "max_violations_per_session": 10000,
            "cleanup_interval_hours": 24,
            "performance_monitoring": True,
            "debug_mode": False
        }
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Created default configuration: {config_path}")
        return default_config
    
    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")
        return {}


def setup_notification_channels(config: Dict[str, Any]) -> NotificationSystem:
    """Setup notification system with configured channels."""
    logger = logging.getLogger(__name__)
    
    notification_system = NotificationSystem()
    
    # Database notification (always enabled)
    db_config = NotificationConfig(
        channel=NotificationChannel.DATABASE,
        enabled=True,
        config={"db_path": "data/violations.db"},
        rate_limit=config.get("notifications", {}).get("rate_limits", {}).get("database", 1000)
    )
    notification_system.add_notification_config(db_config)
    
    # File notification
    file_config = NotificationConfig(
        channel=NotificationChannel.FILE,
        enabled=True,
        config={"file_path": "data/notifications/violations.log"},
        rate_limit=config.get("notifications", {}).get("rate_limits", {}).get("file", 500)
    )
    notification_system.add_notification_config(file_config)
    
    # Email notification (if configured)
    if "email" in config.get("notifications", {}).get("enabled_channels", []):
        email_config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=False,  # Disabled by default, requires manual configuration
            config={
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": []
            },
            rate_limit=config.get("notifications", {}).get("rate_limits", {}).get("email", 10)
        )
        notification_system.add_notification_config(email_config)
    
    logger.info("Configured notification channels")
    return notification_system


def validate_system_setup(base_dir: Path, config: Dict[str, Any]) -> bool:
    """Validate system setup and dependencies."""
    logger = logging.getLogger(__name__)
    
    validation_results = []
    
    # Check directory structure
    required_dirs = [
        base_dir / "data" / "violations",
        base_dir / "data" / "reports",
        base_dir / "logs"
    ]
    
    for directory in required_dirs:
        if directory.exists():
            validation_results.append(f"✓ Directory exists: {directory}")
        else:
            validation_results.append(f"✗ Missing directory: {directory}")
            logger.error(f"Missing directory: {directory}")
    
    # Check database
    db_path = base_dir / "data" / "violations.db"
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            if len(tables) >= 4:  # violations, notifications, sessions, statistics
                validation_results.append(f"✓ Database initialized: {db_path}")
            else:
                validation_results.append(f"✗ Database incomplete: {db_path}")
        except Exception as e:
            validation_results.append(f"✗ Database error: {e}")
    else:
        validation_results.append(f"✗ Database missing: {db_path}")
    
    # Check configuration
    config_path = base_dir / "config" / "violations.json"
    if config_path.exists():
        validation_results.append(f"✓ Configuration exists: {config_path}")
    else:
        validation_results.append(f"✗ Configuration missing: {config_path}")
    
    # Test violation detector
    try:
        detector = ViolationDetector()
        validation_results.append("✓ ViolationDetector initialization successful")
    except Exception as e:
        validation_results.append(f"✗ ViolationDetector error: {e}")
    
    # Test lane detector
    try:
        lane_detector = LaneDetector(
            config.get("lane_detection", {}).get("image_width", 1920),
            config.get("lane_detection", {}).get("image_height", 1080)
        )
        validation_results.append("✓ LaneDetector initialization successful")
    except Exception as e:
        validation_results.append(f"✗ LaneDetector error: {e}")
    
    # Test notification system
    try:
        notification_system = setup_notification_channels(config)
        validation_results.append("✓ NotificationSystem initialization successful")
    except Exception as e:
        validation_results.append(f"✗ NotificationSystem error: {e}")
    
    # Test violation manager
    try:
        manager = ViolationManager()
        manager.db_path = str(db_path)
        validation_results.append("✓ ViolationManager initialization successful")
    except Exception as e:
        validation_results.append(f"✗ ViolationManager error: {e}")
    
    # Print validation results
    print("\n" + "="*60)
    print("VIOLATIONS SYSTEM VALIDATION RESULTS")
    print("="*60)
    
    for result in validation_results:
        print(result)
        logger.info(result.replace("✓", "PASS").replace("✗", "FAIL"))
    
    # Determine overall success
    failed_validations = [r for r in validation_results if "✗" in r]
    success = len(failed_validations) == 0
    
    print(f"\nValidation {'PASSED' if success else 'FAILED'}")
    if not success:
        print(f"Failed validations: {len(failed_validations)}")
    
    return success


def create_sample_data(manager: ViolationManager) -> None:
    """Create sample violation data for testing."""
    logger = logging.getLogger(__name__)
    
    try:
        from src.violations.violation_detector import TrafficViolation, ViolationLocation
        import time
        
        sample_violations = [
            TrafficViolation(
                violation_id="sample_001",
                timestamp=time.time(),
                violation_type=ViolationType.SPEED_VIOLATION,
                severity=ViolationSeverity.MODERATE,
                vehicle_id=1,
                description="Sample speed violation for testing",
                confidence=0.9,
                location=ViolationLocation("zone_1", "Test Zone 1", (100, 100)),
                speed_limit=50.0,
                measured_speed=75.0
            ),
            TrafficViolation(
                violation_id="sample_002", 
                timestamp=time.time() - 300,
                violation_type=ViolationType.LANE_VIOLATION,
                severity=ViolationSeverity.MINOR,
                vehicle_id=2,
                description="Sample lane violation for testing",
                confidence=0.8,
                location=ViolationLocation("zone_2", "Test Zone 2", (200, 200))
            )
        ]
        
        for violation in sample_violations:
            manager._store_violation(violation)
        
        logger.info(f"Created {len(sample_violations)} sample violations")
        print(f"Created {len(sample_violations)} sample violations for testing")
    
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")


def main():
    """Main initialization function."""
    parser = argparse.ArgumentParser(description="Initialize Traffic Violations Detection System")
    parser.add_argument("--base-dir", type=str, default=".", 
                       help="Base directory for system installation")
    parser.add_argument("--log-level", type=str, default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    parser.add_argument("--create-sample-data", action="store_true",
                       help="Create sample violation data for testing")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip system validation")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Convert base directory to Path
    base_dir = Path(args.base_dir).resolve()
    
    print("="*60)
    print("TRAFFIC VIOLATIONS DETECTION SYSTEM INITIALIZATION")
    print("="*60)
    print(f"Base directory: {base_dir}")
    print(f"Log level: {args.log_level}")
    
    try:
        # Step 1: Create directory structure
        print("\n1. Creating directory structure...")
        create_directory_structure(base_dir)
        
        # Step 2: Create configuration
        print("\n2. Creating configuration...")
        config_path = base_dir / "config" / "violations.json"
        config = create_default_config(config_path)
        
        # Step 3: Initialize database
        print("\n3. Initializing database...")
        db_path = base_dir / "data" / "violations.db"
        db_success = initialize_violation_database(db_path)
        
        if not db_success:
            print("✗ Database initialization failed")
            return 1
        
        # Step 4: Setup notification system
        print("\n4. Setting up notification system...")
        notification_system = setup_notification_channels(config)
        
        # Step 5: Create sample data (if requested)
        if args.create_sample_data:
            print("\n5. Creating sample data...")
            manager = ViolationManager()
            manager.db_path = str(db_path)
            create_sample_data(manager)
        
        # Step 6: Validate system (if not skipped)
        if not args.skip_validation:
            print("\n6. Validating system setup...")
            validation_success = validate_system_setup(base_dir, config)
            
            if not validation_success:
                print("\n✗ System validation failed")
                return 1
        
        # Success message
        print("\n" + "="*60)
        print("INITIALIZATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"System installed in: {base_dir}")
        print(f"Database: {db_path}")
        print(f"Configuration: {config_path}")
        print(f"Logs: {base_dir / 'logs'}")
        
        print("\nNext steps:")
        print("1. Review and customize configuration in config/violations.json")
        print("2. Configure notification channels (email, SMS, etc.)")
        print("3. Test the system with sample traffic data")
        print("4. Monitor logs for any issues")
        
        return 0
    
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        print(f"\n✗ Initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())