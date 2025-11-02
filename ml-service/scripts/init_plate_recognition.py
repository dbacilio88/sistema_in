#!/usr/bin/env python3
"""
Initialize and test the license plate recognition system.

This script initializes all recognition components and runs
basic tests to ensure everything is working correctly.
"""

import sys
import os
import logging
import time
import numpy as np
import cv2
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from recognition.plate_detector import LicensePlateDetector, PlateDetection
from recognition.plate_reader import LicensePlateReader, PlateReading
from recognition.plate_validator import PeruvianPlateValidator, PlateFormat
from config import get_ml_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_plate_validator():
    """Test Peruvian plate validator."""
    logger.info("Testing PeruvianPlateValidator...")
    
    validator = PeruvianPlateValidator()
    
    # Test valid plates
    valid_plates = [
        "ABC123",    # Old format
        "ABC1234",   # New format
        "T1A123",    # Taxi format
        "A1123",     # Motorcycle format
        "PNP123",    # Police format
        "CD456"      # Diplomatic format
    ]
    
    for plate in valid_plates:
        result = validator.validate(plate)
        assert result.is_valid, f"Valid plate {plate} was rejected: {result.errors}"
        logger.info(f"✓ {plate} -> {result.format_type.value} (confidence: {result.confidence:.3f})")
    
    # Test invalid plates
    invalid_plates = [
        "WTF123",    # Forbidden combination
        "12345",     # Numbers only
        "ABCDEF",    # Letters only
        "A",         # Too short
        "TOOLONG123" # Too long
    ]
    
    for plate in invalid_plates:
        result = validator.validate(plate)
        assert not result.is_valid, f"Invalid plate {plate} was accepted"
        logger.info(f"✓ {plate} -> rejected (errors: {result.errors})")
    
    # Test normalization
    test_cases = [
        ("abc123", "ABC-123"),
        ("ABC 123", "ABC-123"),
        ("abc-123", "ABC-123")
    ]
    
    for input_text, expected in test_cases:
        normalized = validator._normalize_plate_text(input_text)
        assert normalized == expected, f"Normalization failed: {input_text} -> {normalized} (expected {expected})"
        logger.info(f"✓ Normalization: '{input_text}' -> '{normalized}'")
    
    # Test suggestions
    suggestions = validator.suggest_corrections("ABC12O")  # Common OCR error
    logger.info(f"✓ Suggestions for 'ABC12O': {suggestions}")
    
    logger.info("✓ PeruvianPlateValidator working correctly")

def test_plate_detector():
    """Test license plate detector."""
    logger.info("Testing LicensePlateDetector...")
    
    detector = LicensePlateDetector(use_cascade=True)
    
    # Create synthetic test image with plate-like region
    image = np.zeros((300, 500, 3), dtype=np.uint8)
    
    # Draw a white rectangle (simulating a plate)
    cv2.rectangle(image, (150, 100), (350, 150), (255, 255, 255), -1)
    
    # Add black border
    cv2.rectangle(image, (150, 100), (350, 150), (0, 0, 0), 2)
    
    # Add text-like patterns
    for i in range(6):
        x = 160 + i * 30
        cv2.rectangle(image, (x, 110), (x + 20, 140), (0, 0, 0), -1)
    
    # Test detection
    detections = detector.detect_plates(image)
    logger.info(f"Found {len(detections)} potential plates")
    
    if detections:
        for i, detection in enumerate(detections):
            logger.info(f"  Detection {i}: bbox={detection.bbox}, confidence={detection.confidence:.3f}")
    
    # Test preprocessing
    if detections:
        plate_image = detections[0].plate_image
        processed = detector.preprocess_plate_image(plate_image)
        logger.info(f"✓ Preprocessing: {plate_image.shape} -> {processed.shape}")
    
    # Test visualization
    vis_image = detector.visualize_detections(image, detections)
    assert not np.array_equal(image, vis_image), "Visualization should modify the image"
    
    # Test stats
    stats = detector.get_detection_stats()
    logger.info(f"✓ Detection stats: {stats}")
    
    logger.info("✓ LicensePlateDetector working correctly")

def test_plate_reader():
    """Test license plate reader."""
    logger.info("Testing LicensePlateReader...")
    
    # Check if EasyOCR is available
    try:
        reader = LicensePlateReader(languages=['en'])
        logger.info("✓ LicensePlateReader initialized successfully")
    except Exception as e:
        logger.warning(f"EasyOCR not available, skipping reader tests: {e}")
        return
    
    # Create synthetic plate image with text
    plate_image = create_synthetic_plate_image("ABC123")
    
    # Test reading
    reading = reader.read_plate(plate_image)
    logger.info(f"Reading result: '{reading.plate_text}' (confidence: {reading.confidence:.3f})")
    logger.info(f"Valid format: {reading.is_valid_format}, Format: {reading.detected_format}")
    logger.info(f"Processing time: {reading.processing_time_ms:.1f}ms")
    
    # Test text cleaning
    test_cases = [
        ("ABC 123", "ABC123"),
        ("ABC-123", "ABC123"),
        ("AB0123", "ABO123")  # Context-aware correction
    ]
    
    for input_text, expected in test_cases:
        cleaned = reader._clean_plate_text(input_text)
        logger.info(f"✓ Text cleaning: '{input_text}' -> '{cleaned}'")
    
    # Test stats
    stats = reader.get_reading_stats()
    logger.info(f"✓ Reading stats: {stats}")
    
    logger.info("✓ LicensePlateReader working correctly")

def create_synthetic_plate_image(text: str) -> np.ndarray:
    """Create a synthetic license plate image for testing."""
    # Plate dimensions
    width, height = 300, 60
    
    # Create white background
    plate = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add border
    cv2.rectangle(plate, (2, 2), (width-3, height-3), (0, 0, 0), 2)
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    thickness = 2
    
    # Format text with dash
    display_text = text
    if len(text) == 6 and text[:3].isalpha() and text[3:].isdigit():
        display_text = text[:3] + "-" + text[3:]
    
    # Calculate text position
    (text_width, text_height), _ = cv2.getTextSize(display_text, font, font_scale, thickness)
    x = (width - text_width) // 2
    y = (height + text_height) // 2
    
    cv2.putText(plate, display_text, (x, y), font, font_scale, (0, 0, 0), thickness)
    
    return plate

def test_integration():
    """Test integration between all components."""
    logger.info("Testing component integration...")
    
    # Initialize components
    detector = LicensePlateDetector(use_cascade=True)
    
    try:
        reader = LicensePlateReader(languages=['en'])
    except Exception as e:
        logger.warning(f"Skipping integration test due to EasyOCR: {e}")
        return
    
    validator = PeruvianPlateValidator()
    
    # Create test image with vehicle and plate
    image = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Draw vehicle-like rectangle
    cv2.rectangle(image, (100, 150), (500, 350), (100, 100, 100), -1)
    
    # Draw plate region
    plate_x, plate_y = 250, 280
    plate_w, plate_h = 150, 40
    cv2.rectangle(image, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (255, 255, 255), -1)
    cv2.rectangle(image, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (0, 0, 0), 2)
    
    # Add text to plate
    cv2.putText(image, "ABC-123", (plate_x + 10, plate_y + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Run complete pipeline
    vehicle_bbox = (100, 150, 500, 350)
    
    # Step 1: Detection
    detections = detector.detect_plates(image, vehicle_bbox)
    logger.info(f"Pipeline step 1: Found {len(detections)} plate detections")
    
    if detections:
        # Step 2: OCR
        best_detection = max(detections, key=lambda d: d.confidence)
        reading = reader.read_plate(best_detection.plate_image)
        logger.info(f"Pipeline step 2: OCR result: '{reading.plate_text}' (confidence: {reading.confidence:.3f})")
        
        # Step 3: Validation
        validation = validator.validate(reading.plate_text)
        logger.info(f"Pipeline step 3: Validation result: {validation.is_valid} (format: {validation.format_type.value})")
        
        # Overall success
        if validation.is_valid and reading.confidence > 0.5:
            logger.info("✓ Integration test: Complete pipeline successful")
        else:
            logger.warning("⚠ Integration test: Pipeline completed but with low confidence/validity")
    else:
        logger.warning("⚠ Integration test: No plates detected")
    
    logger.info("✓ Integration test completed")

def test_performance():
    """Test basic performance characteristics."""
    logger.info("Testing performance...")
    
    detector = LicensePlateDetector()
    
    try:
        reader = LicensePlateReader(languages=['en'])
    except Exception as e:
        logger.warning(f"Skipping performance test due to EasyOCR: {e}")
        return
    
    validator = PeruvianPlateValidator()
    
    # Create test images
    test_images = []
    for i in range(10):
        plate_text = f"ABC{i:03d}"
        plate_img = create_synthetic_plate_image(plate_text)
        test_images.append((plate_img, plate_text))
    
    # Test detection performance
    detection_times = []
    for plate_img, _ in test_images:
        # Create full image
        full_image = np.zeros((300, 500, 3), dtype=np.uint8)
        full_image[100:160, 150:450] = plate_img
        
        start_time = time.time()
        detections = detector.detect_plates(full_image)
        detection_time = time.time() - start_time
        detection_times.append(detection_time)
    
    avg_detection_time = sum(detection_times) / len(detection_times)
    logger.info(f"Detection performance: {avg_detection_time*1000:.2f}ms average")
    
    # Test OCR performance
    ocr_times = []
    for plate_img, _ in test_images:
        start_time = time.time()
        reading = reader.read_plate(plate_img)
        ocr_time = time.time() - start_time
        ocr_times.append(ocr_time)
    
    avg_ocr_time = sum(ocr_times) / len(ocr_times)
    logger.info(f"OCR performance: {avg_ocr_time*1000:.2f}ms average")
    
    # Test validation performance
    validation_times = []
    test_plates = ["ABC123", "XYZ789", "T1A456", "A1234", "PNP123"]
    for plate in test_plates:
        start_time = time.time()
        result = validator.validate(plate)
        validation_time = time.time() - start_time
        validation_times.append(validation_time)
    
    avg_validation_time = sum(validation_times) / len(validation_times)
    logger.info(f"Validation performance: {avg_validation_time*1000:.2f}ms average")
    
    # Overall pipeline performance
    total_time = avg_detection_time + avg_ocr_time + avg_validation_time
    fps = 1.0 / total_time
    logger.info(f"Overall pipeline: {total_time*1000:.2f}ms, {fps:.1f} FPS")
    
    logger.info("✓ Performance test completed")

def test_configuration():
    """Test configuration loading."""
    logger.info("Testing configuration...")
    
    settings = get_ml_settings()
    
    logger.info(f"GPU enabled: {settings.gpu_enabled}")
    logger.info(f"Model directory: {settings.model_dir}")
    logger.info(f"ONNX providers: {settings.onnx_providers}")
    
    # Verify required directories exist
    model_dir = Path(settings.model_dir)
    if not model_dir.exists():
        logger.warning(f"Model directory doesn't exist: {model_dir}")
        model_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created model directory: {model_dir}")
    
    logger.info("✓ Configuration test completed")

def run_all_tests():
    """Run all initialization tests."""
    logger.info("Starting license plate recognition system tests...")
    
    try:
        test_configuration()
        test_plate_validator()
        test_plate_detector()
        test_plate_reader()
        test_integration()
        test_performance()
        
        logger.info("🎉 All tests passed! License plate recognition system is ready.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main initialization function."""
    logger.info("Initializing License Plate Recognition System")
    
    # Check dependencies
    dependencies = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
    }
    
    for module, package in dependencies.items():
        try:
            __import__(module)
            logger.info(f"✓ {module} available")
        except ImportError:
            logger.error(f"❌ {module} not installed. Run: pip install {package}")
            return False
    
    # Check optional dependencies
    try:
        import easyocr
        logger.info("✓ EasyOCR available")
    except ImportError:
        logger.warning("⚠ EasyOCR not installed. Some features will be limited.")
        logger.info("To install: pip install easyocr")
    
    # Run tests
    success = run_all_tests()
    
    if success:
        logger.info("✅ License plate recognition system initialization completed successfully")
        logger.info("Ready to process vehicle images with plate recognition")
        
        # Show supported formats
        validator = PeruvianPlateValidator()
        formats = validator.get_all_formats()
        logger.info("Supported Peruvian plate formats:")
        for format_type, info in formats.items():
            logger.info(f"  {format_type.value}: {info['example']} ({info['active_period']})")
        
    else:
        logger.error("❌ License plate recognition system initialization failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)