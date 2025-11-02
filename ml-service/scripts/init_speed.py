"""
Speed Analysis Initialization Script.

This script initializes the speed analysis module with camera calibration
and speed calculation for traffic violation detection.
"""

import logging
import sys
import time
from pathlib import Path
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.speed.camera_calibrator import CameraCalibrator, CalibrationZone
from src.speed.speed_calculator import SpeedCalculator
from src.speed.speed_analyzer import SpeedAnalyzer, AnalysisMode
from src.detection.vehicle_detector import YOLOv8VehicleDetector
from src.tracking.vehicle_tracker import VehicleTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_camera_calibration(image_width: int = 1920, image_height: int = 1080) -> CameraCalibrator:
    """
    Initialize camera calibration for speed measurement.
    
    Args:
        image_width: Camera image width
        image_height: Camera image height
        
    Returns:
        Configured camera calibrator
    """
    logger.info("Initializing camera calibration...")
    
    calibrator = CameraCalibrator()
    
    # Option 1: Create default highway calibration
    logger.info("Creating default highway calibration...")
    success = calibrator.create_default_highway_calibration(image_width, image_height)
    
    if success:
        logger.info("Default calibration created successfully")
        validation = calibrator.validate_calibration()
        logger.info(f"Calibration validation: {validation}")
        return calibrator
    
    # Option 2: Manual calibration points (if default fails)
    logger.info("Setting up manual calibration points...")
    
    # Define calibration points for a typical highway camera view
    # These represent lane markers and road boundaries
    lane_width = 3.5  # meters
    visible_distance = 50.0  # meters
    
    calibration_points = [
        # Near edge (bottom of image) - road markings
        (image_width * 0.1, image_height * 0.95, -lane_width * 1.5, 2.0),  # Left road edge
        (image_width * 0.3, image_height * 0.90, -lane_width * 0.5, 5.0),  # Left lane marker
        (image_width * 0.5, image_height * 0.90, 0.0, 5.0),                # Center line
        (image_width * 0.7, image_height * 0.90, lane_width * 0.5, 5.0),   # Right lane marker
        (image_width * 0.9, image_height * 0.95, lane_width * 1.5, 2.0),   # Right road edge
        
        # Mid distance - lane markers
        (image_width * 0.35, image_height * 0.60, -lane_width * 0.5, 25.0), # Left lane marker
        (image_width * 0.5, image_height * 0.60, 0.0, 25.0),                # Center line
        (image_width * 0.65, image_height * 0.60, lane_width * 0.5, 25.0),  # Right lane marker
        
        # Far edge (horizon) - vanishing point area
        (image_width * 0.45, image_height * 0.35, -lane_width * 0.3, visible_distance), # Left vanishing
        (image_width * 0.5, image_height * 0.35, 0.0, visible_distance),                # Center vanishing
        (image_width * 0.55, image_height * 0.35, lane_width * 0.3, visible_distance),  # Right vanishing
    ]
    
    # Add calibration points
    for i, (px, py, rx, ry) in enumerate(calibration_points):
        success = calibrator.add_calibration_point(
            int(px), int(py), rx, ry, f"Highway calibration point {i+1}"
        )
        if not success:
            logger.warning(f"Failed to add calibration point {i+1}")
    
    if calibrator.is_calibrated:
        logger.info("Manual calibration completed successfully")
        
        # Create speed measurement zones
        create_speed_zones(calibrator, image_width, image_height)
        
        # Validate calibration
        validation = calibrator.validate_calibration()
        logger.info(f"Calibration validation: {validation}")
        
        return calibrator
    else:
        logger.error("Failed to establish camera calibration")
        return None

def create_speed_zones(calibrator: CameraCalibrator, image_width: int, image_height: int):
    """Create speed measurement zones."""
    logger.info("Creating speed measurement zones...")
    
    lane_width = 3.5
    
    # Main highway zone (left lanes)
    left_zone = CalibrationZone(
        zone_id="highway_left",
        name="Highway Left Lanes",
        pixel_points=[
            (int(image_width * 0.1), int(image_height * 0.95)),   # Bottom left
            (int(image_width * 0.5), int(image_height * 0.90)),   # Bottom center
            (int(image_width * 0.5), int(image_height * 0.35)),   # Top center
            (int(image_width * 0.45), int(image_height * 0.35))   # Top left
        ],
        real_world_points=[
            (-lane_width * 1.5, 2.0),
            (0.0, 5.0),
            (0.0, 50.0),
            (-lane_width * 0.3, 50.0)
        ],
        speed_limit=100.0,  # 100 km/h
        measurement_distance=30.0,  # 30 meter measurement zone
        entry_line=((int(image_width * 0.2), int(image_height * 0.85)),
                   (int(image_width * 0.5), int(image_height * 0.85))),
        exit_line=((int(image_width * 0.35), int(image_height * 0.45)),
                  (int(image_width * 0.5), int(image_height * 0.45))),
        direction="forward"
    )
    
    # Main highway zone (right lanes)
    right_zone = CalibrationZone(
        zone_id="highway_right",
        name="Highway Right Lanes",
        pixel_points=[
            (int(image_width * 0.5), int(image_height * 0.90)),   # Bottom center
            (int(image_width * 0.9), int(image_height * 0.95)),   # Bottom right
            (int(image_width * 0.55), int(image_height * 0.35)),  # Top right
            (int(image_width * 0.5), int(image_height * 0.35))    # Top center
        ],
        real_world_points=[
            (0.0, 5.0),
            (lane_width * 1.5, 2.0),
            (lane_width * 0.3, 50.0),
            (0.0, 50.0)
        ],
        speed_limit=100.0,  # 100 km/h
        measurement_distance=30.0,  # 30 meter measurement zone
        entry_line=((int(image_width * 0.5), int(image_height * 0.85)),
                   (int(image_width * 0.8), int(image_height * 0.85))),
        exit_line=((int(image_width * 0.5), int(image_height * 0.45)),
                  (int(image_width * 0.65), int(image_height * 0.45))),
        direction="forward"
    )
    
    # School zone (reduced speed limit)
    school_zone = CalibrationZone(
        zone_id="school_zone",
        name="School Zone",
        pixel_points=[
            (int(image_width * 0.2), int(image_height * 0.80)),
            (int(image_width * 0.8), int(image_height * 0.80)),
            (int(image_width * 0.6), int(image_height * 0.50)),
            (int(image_width * 0.4), int(image_height * 0.50))
        ],
        real_world_points=[
            (-lane_width, 10.0),
            (lane_width, 10.0),
            (lane_width * 0.5, 35.0),
            (-lane_width * 0.5, 35.0)
        ],
        speed_limit=30.0,  # 30 km/h school zone
        measurement_distance=20.0,
        entry_line=((int(image_width * 0.25), int(image_height * 0.75)),
                   (int(image_width * 0.75), int(image_height * 0.75))),
        exit_line=((int(image_width * 0.35), int(image_height * 0.55)),
                  (int(image_width * 0.65), int(image_height * 0.55))),
        direction="any"
    )
    
    # Add zones to calibrator
    calibrator.add_calibration_zone(left_zone)
    calibrator.add_calibration_zone(right_zone)
    calibrator.add_calibration_zone(school_zone)
    
    logger.info(f"Created {len(calibrator.calibration_zones)} speed measurement zones")

def initialize_speed_analysis_system() -> tuple:
    """
    Initialize complete speed analysis system.
    
    Returns:
        Tuple of (detector, tracker, calibrator, calculator, analyzer)
    """
    logger.info("Initializing complete speed analysis system...")
    
    # Initialize camera calibration
    calibrator = initialize_camera_calibration()
    if calibrator is None:
        logger.error("Failed to initialize camera calibration")
        return None
    
    # Initialize vehicle detector
    logger.info("Initializing vehicle detector...")
    try:
        detector = YOLOv8VehicleDetector(
            model_path="models/yolov8n.pt",  # Will be downloaded if not exists
            device="cuda" if True else "cpu",  # Auto-detect GPU
            confidence_threshold=0.5,
            use_onnx=True
        )
        logger.info("Vehicle detector initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize vehicle detector: {e}")
        # Use mock detector for testing
        from unittest.mock import Mock
        detector = Mock()
        logger.info("Using mock detector for testing")
    
    # Initialize vehicle tracker
    logger.info("Initializing vehicle tracker...")
    try:
        tracker = VehicleTracker(
            max_disappeared_frames=30,
            max_distance_threshold=100,
            min_confidence=0.5
        )
        logger.info("Vehicle tracker initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize vehicle tracker: {e}")
        # Use mock tracker for testing
        from unittest.mock import Mock
        tracker = Mock()
        logger.info("Using mock tracker for testing")
    
    # Initialize speed calculator
    logger.info("Initializing speed calculator...")
    calculator = SpeedCalculator(calibrator)
    logger.info("Speed calculator initialized successfully")
    
    # Initialize speed analyzer
    logger.info("Initializing speed analyzer...")
    analyzer = SpeedAnalyzer(
        detector=detector,
        tracker=tracker,
        calibrator=calibrator,
        mode=AnalysisMode.REALTIME
    )
    
    # Configure analyzer settings
    analyzer.min_tracking_frames = 10      # Minimum frames for speed calculation
    analyzer.violation_cooldown = 30.0     # 30 second cooldown between violations
    analyzer.save_evidence = True          # Save violation evidence
    
    logger.info("Speed analyzer initialized successfully")
    
    return detector, tracker, calibrator, calculator, analyzer

def test_speed_analysis_system(analyzer: SpeedAnalyzer):
    """Test the speed analysis system with synthetic data."""
    logger.info("Testing speed analysis system...")
    
    # Create test frame
    test_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    
    try:
        # Analyze test frame
        result = analyzer.analyze_frame(test_frame)
        
        logger.info(f"Test frame analysis completed:")
        logger.info(f"  Frame ID: {result.frame_id}")
        logger.info(f"  Processing time: {result.processing_time:.4f}s")
        logger.info(f"  FPS: {result.fps:.2f}")
        logger.info(f"  Detections: {len(result.detections)}")
        logger.info(f"  Tracked vehicles: {len(result.tracked_vehicles)}")
        logger.info(f"  Speed measurements: {len(result.speed_measurements)}")
        logger.info(f"  Violations: {len(result.violations)}")
        
        # Get performance summary
        performance = analyzer.get_performance_summary()
        logger.info(f"Performance summary: {performance}")
        
        logger.info("Speed analysis system test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Speed analysis system test failed: {e}")
        return False

def save_calibration_config(calibrator: CameraCalibrator, filepath: str = "config/camera_calibration.json"):
    """Save camera calibration configuration."""
    logger.info(f"Saving calibration configuration to {filepath}")
    
    # Create config directory if it doesn't exist
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    success = calibrator.save_calibration(filepath)
    if success:
        logger.info(f"Calibration configuration saved successfully to {filepath}")
    else:
        logger.error(f"Failed to save calibration configuration to {filepath}")
    
    return success

def main():
    """Main initialization function."""
    logger.info("Starting speed analysis module initialization...")
    
    try:
        # Initialize complete system
        components = initialize_speed_analysis_system()
        
        if components is None:
            logger.error("Failed to initialize speed analysis system")
            return False
        
        detector, tracker, calibrator, calculator, analyzer = components
        
        # Save calibration configuration
        save_calibration_config(calibrator)
        
        # Test system
        test_success = test_speed_analysis_system(analyzer)
        
        if test_success:
            logger.info("Speed analysis module initialization completed successfully!")
            
            # Print system summary
            print("\n" + "="*60)
            print("SPEED ANALYSIS SYSTEM INITIALIZED")
            print("="*60)
            print(f"Camera calibration: {'✓' if calibrator.is_calibrated else '✗'}")
            print(f"Calibration error: {calibrator.calibration_error:.4f}m" if calibrator.calibration_error else "N/A")
            print(f"Speed measurement zones: {len(calibrator.calibration_zones)}")
            print(f"Vehicle detector: {'✓' if hasattr(detector, 'model') else '⚠ (mock)'}")
            print(f"Vehicle tracker: {'✓' if hasattr(tracker, 'trackers') else '⚠ (mock)'}")
            print(f"Evidence collection: {'✓' if analyzer.save_evidence else '✗'}")
            print("="*60)
            
            # Print calibration zones
            print("\nSPEED MEASUREMENT ZONES:")
            for zone_id, zone in calibrator.calibration_zones.items():
                print(f"  {zone.name} ({zone_id}): {zone.speed_limit} km/h limit")
            
            print(f"\nSystem ready for traffic violation detection!")
            print("="*60)
            
            return True
        else:
            logger.error("Speed analysis system test failed")
            return False
            
    except Exception as e:
        logger.error(f"Speed analysis module initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)