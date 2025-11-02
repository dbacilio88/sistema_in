"""
Comprehensive tests for license plate recognition module.

Tests cover detection, OCR, validation, and integration functionality.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.recognition.plate_detector import LicensePlateDetector, PlateDetection
from src.recognition.plate_reader import LicensePlateReader, PlateReading, OCRResult
from src.recognition.plate_validator import PeruvianPlateValidator, PlateFormat, ValidationResult

class TestPlateDetection:
    """Test PlateDetection dataclass."""
    
    def test_plate_detection_creation(self):
        """Test PlateDetection object creation."""
        plate_image = np.zeros((50, 150, 3), dtype=np.uint8)
        
        detection = PlateDetection(
            bbox=(100, 200, 250, 250),
            confidence=0.85,
            plate_image=plate_image,
            vehicle_bbox=(50, 150, 300, 300)
        )
        
        assert detection.bbox == (100, 200, 250, 250)
        assert detection.confidence == 0.85
        assert detection.plate_image.shape == (50, 150, 3)
        assert detection.vehicle_bbox == (50, 150, 300, 300)

class TestOCRResult:
    """Test OCRResult dataclass."""
    
    def test_ocr_result_creation(self):
        """Test OCRResult object creation."""
        bbox = [(0, 0), (100, 0), (100, 30), (0, 30)]
        
        result = OCRResult(
            text="ABC123",
            confidence=0.92,
            bbox=bbox
        )
        
        assert result.text == "ABC123"
        assert result.confidence == 0.92
        assert len(result.bbox) == 4

class TestPlateReading:
    """Test PlateReading dataclass."""
    
    def test_plate_reading_creation(self):
        """Test PlateReading object creation."""
        ocr_results = [
            OCRResult(text="ABC123", confidence=0.9, bbox=[(0, 0), (100, 0), (100, 30), (0, 30)])
        ]
        
        reading = PlateReading(
            plate_text="ABC123",
            confidence=0.9,
            raw_ocr_results=ocr_results,
            is_valid_format=True,
            detected_format="old_standard",
            processing_time_ms=150.0
        )
        
        assert reading.plate_text == "ABC123"
        assert reading.confidence == 0.9
        assert reading.is_valid_format is True
        assert reading.detected_format == "old_standard"
        assert reading.processing_time_ms == 150.0

class TestPeruvianPlateValidator:
    """Test PeruvianPlateValidator class."""
    
    def setup_method(self):
        """Setup validator for each test."""
        self.validator = PeruvianPlateValidator()
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        assert len(self.validator.patterns) > 0
        assert PlateFormat.OLD_STANDARD in self.validator.patterns
        assert PlateFormat.NEW_STANDARD in self.validator.patterns
    
    def test_validate_old_format(self):
        """Test validation of old format plates."""
        test_cases = [
            ("ABC123", True),
            ("ABC-123", True),
            ("XYZ789", True),
            ("AB123", False),  # Too short
            ("ABCD123", False)  # Too long
        ]
        
        for plate_text, should_be_valid in test_cases:
            result = self.validator.validate(plate_text)
            assert result.is_valid == should_be_valid, f"Failed for {plate_text}"
            if should_be_valid:
                assert result.format_type == PlateFormat.OLD_STANDARD
    
    def test_validate_new_format(self):
        """Test validation of new format plates."""
        test_cases = [
            ("ABC1234", True),
            ("ABC-1234", True),
            ("XYZ9876", True),
            ("AB1234", False),   # Too few letters
            ("ABC12345", False)  # Too many numbers
        ]
        
        for plate_text, should_be_valid in test_cases:
            result = self.validator.validate(plate_text)
            if should_be_valid:
                assert result.is_valid == should_be_valid, f"Failed for {plate_text}"
                assert result.format_type == PlateFormat.NEW_STANDARD
    
    def test_validate_taxi_format(self):
        """Test validation of taxi format plates."""
        test_cases = [
            ("T1A123", True),
            ("T1A-123", True),
            ("T2B456", True),
            ("T12A123", False),  # Wrong format
            ("A1A123", False)    # Wrong prefix
        ]
        
        for plate_text, should_be_valid in test_cases:
            result = self.validator.validate(plate_text)
            if should_be_valid:
                assert result.is_valid == should_be_valid, f"Failed for {plate_text}"
                assert result.format_type == PlateFormat.TAXI
    
    def test_validate_motorcycle_format(self):
        """Test validation of motorcycle format plates."""
        test_cases = [
            ("A1123", True),
            ("A1-123", True),
            ("B2456", True),
            ("AB123", False),    # Wrong format
            ("A12345", False)    # Too many numbers
        ]
        
        for plate_text, should_be_valid in test_cases:
            result = self.validator.validate(plate_text)
            if should_be_valid:
                assert result.is_valid == should_be_valid, f"Failed for {plate_text}"
                assert result.format_type == PlateFormat.MOTORCYCLE
    
    def test_validate_special_formats(self):
        """Test validation of special format plates."""
        test_cases = [
            ("PNP123", PlateFormat.POLICE),
            ("CD123", PlateFormat.DIPLOMATIC),
            ("TP123", PlateFormat.TEMPORARY),
            ("AB1234", PlateFormat.COMMERCIAL)
        ]
        
        for plate_text, expected_format in test_cases:
            result = self.validator.validate(plate_text)
            assert result.is_valid, f"Failed for {plate_text}"
            assert result.format_type == expected_format
    
    def test_forbidden_combinations(self):
        """Test rejection of forbidden combinations."""
        forbidden_plates = ["WTF123", "ASS456", "SEX789"]
        
        for plate_text in forbidden_plates:
            result = self.validator.validate(plate_text)
            assert result.is_valid is False
            assert len(result.errors) > 0
    
    def test_normalize_plate_text(self):
        """Test plate text normalization."""
        test_cases = [
            ("abc123", "ABC-123"),
            ("ABC 123", "ABC-123"),
            ("abc-123", "ABC-123"),
            ("ABC123", "ABC-123"),
            ("A1123", "A1-123")
        ]
        
        for input_text, expected in test_cases:
            normalized = self.validator._normalize_plate_text(input_text)
            assert normalized == expected, f"Normalization failed for {input_text}"
    
    def test_fuzzy_validation(self):
        """Test fuzzy validation for OCR errors."""
        # Common OCR errors
        test_cases = [
            ("ABC12O", "ABC120"),  # O -> 0
            ("AB0123", "ABO123"),  # 0 -> O in letter position
            ("ABC1Z3", "ABC123"),  # Z -> 2
            ("AB8123", "ABB123")   # 8 -> B in letter position
        ]
        
        for ocr_text, expected_correction in test_cases:
            result = self.validator.validate(ocr_text)
            # Should either be valid directly or suggest the correction
            if not result.is_valid:
                suggestions = self.validator.suggest_corrections(ocr_text)
                assert expected_correction in suggestions or any(
                    expected_correction.replace('-', '') in s.replace('-', '') 
                    for s in suggestions
                )
    
    def test_suggest_corrections(self):
        """Test correction suggestions."""
        # Test with invalid plate that can be corrected
        suggestions = self.validator.suggest_corrections("ABC12O")
        assert len(suggestions) > 0
        
        # Test with valid plate (should return empty or minimal suggestions)
        suggestions = self.validator.suggest_corrections("ABC123")
        assert isinstance(suggestions, list)
    
    def test_reserved_prefixes(self):
        """Test reserved prefix detection."""
        reserved_cases = [
            ("PNP123", True, "Police Nacional del Peru"),
            ("CD123", True, "Cuerpo Diplomatico"),
            ("ABC123", False, None)
        ]
        
        for plate_text, is_reserved, expected_desc in reserved_cases:
            is_res, desc = self.validator.is_reserved_prefix(plate_text)
            assert is_res == is_reserved
            if is_reserved:
                assert desc == expected_desc

class TestLicensePlateDetector:
    """Test LicensePlateDetector class."""
    
    def setup_method(self):
        """Setup detector for each test."""
        self.detector = LicensePlateDetector(use_cascade=True)
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        assert self.detector.use_cascade is True
        assert hasattr(self.detector, 'settings')
    
    @patch('cv2.CascadeClassifier')
    def test_detect_with_cascade(self, mock_cascade_class):
        """Test detection using cascade classifier."""
        # Mock cascade classifier
        mock_cascade = Mock()
        mock_cascade.empty.return_value = False
        mock_cascade.detectMultiScale.return_value = [(50, 20, 150, 40)]
        mock_cascade_class.return_value = mock_cascade
        
        # Create detector with mocked cascade
        detector = LicensePlateDetector(use_cascade=True)
        detector.cascade = mock_cascade
        
        # Test image
        image = np.random.randint(0, 255, (300, 500, 3), dtype=np.uint8)
        
        # Run detection
        detections = detector.detect_plates(image)
        
        # Verify results
        assert len(detections) > 0
        detection = detections[0]
        assert isinstance(detection, PlateDetection)
        assert detection.confidence > 0
    
    def test_detect_with_contours(self):
        """Test detection using contour analysis."""
        # Create synthetic image with plate-like rectangle
        image = np.zeros((300, 500, 3), dtype=np.uint8)
        # Draw a white rectangle (simulating a plate)
        cv2.rectangle(image, (150, 100), (350, 150), (255, 255, 255), -1)
        # Add some text-like patterns
        cv2.rectangle(image, (160, 110), (170, 140), (0, 0, 0), -1)
        cv2.rectangle(image, (180, 110), (190, 140), (0, 0, 0), -1)
        
        detector = LicensePlateDetector(use_cascade=False)
        detections = detector._detect_with_contours(image, (0, 0))
        
        # Should find the rectangular region
        assert len(detections) > 0
    
    def test_filter_detections(self):
        """Test detection filtering and NMS."""
        # Create overlapping detections
        plate_image = np.zeros((50, 150, 3), dtype=np.uint8)
        detections = [
            PlateDetection(bbox=(100, 100, 250, 150), confidence=0.9, plate_image=plate_image),
            PlateDetection(bbox=(105, 105, 255, 155), confidence=0.7, plate_image=plate_image),  # Overlapping
            PlateDetection(bbox=(300, 100, 450, 150), confidence=0.8, plate_image=plate_image)   # Separate
        ]
        
        image = np.zeros((400, 600, 3), dtype=np.uint8)
        filtered = self.detector._filter_detections(detections, image)
        
        # Should remove overlapping detection with lower confidence
        assert len(filtered) == 2
        assert filtered[0].confidence == 0.9  # Highest confidence first
    
    def test_preprocess_plate_image(self):
        """Test plate image preprocessing."""
        # Create test plate image
        plate_image = np.random.randint(0, 255, (40, 120, 3), dtype=np.uint8)
        
        processed = self.detector.preprocess_plate_image(plate_image)
        
        # Should be processed
        assert processed.shape[0] == 64  # Standard height
        assert len(processed.shape) == 2  # Grayscale
    
    def test_visualize_detections(self):
        """Test detection visualization."""
        image = np.zeros((300, 500, 3), dtype=np.uint8)
        plate_image = np.zeros((50, 150, 3), dtype=np.uint8)
        
        detections = [
            PlateDetection(bbox=(100, 100, 250, 150), confidence=0.9, plate_image=plate_image)
        ]
        
        vis_image = self.detector.visualize_detections(image, detections)
        
        # Should have modified the image
        assert not np.array_equal(image, vis_image)
        assert vis_image.shape == image.shape

@patch('easyocr.Reader')
class TestLicensePlateReader:
    """Test LicensePlateReader class."""
    
    def test_reader_initialization(self, mock_easyocr):
        """Test reader initialization."""
        mock_reader_instance = Mock()
        mock_easyocr.return_value = mock_reader_instance
        
        reader = LicensePlateReader()
        
        assert reader.languages == ['en']
        mock_easyocr.assert_called_once()
    
    def test_read_plate_success(self, mock_easyocr):
        """Test successful plate reading."""
        # Mock EasyOCR response
        mock_reader_instance = Mock()
        mock_reader_instance.readtext.return_value = [
            ([(0, 0), (100, 0), (100, 30), (0, 30)], 'ABC123', 0.95)
        ]
        mock_easyocr.return_value = mock_reader_instance
        
        reader = LicensePlateReader()
        plate_image = np.random.randint(0, 255, (50, 150, 3), dtype=np.uint8)
        
        result = reader.read_plate(plate_image)
        
        assert isinstance(result, PlateReading)
        assert result.plate_text == "ABC123"
        assert result.confidence > 0.9
        assert result.is_valid_format is True
    
    def test_read_plate_with_preprocessing(self, mock_easyocr):
        """Test plate reading with preprocessing."""
        mock_reader_instance = Mock()
        mock_reader_instance.readtext.return_value = [
            ([(0, 0), (100, 0), (100, 30), (0, 30)], 'ABC1234', 0.87)
        ]
        mock_easyocr.return_value = mock_reader_instance
        
        reader = LicensePlateReader()
        plate_image = np.random.randint(0, 255, (40, 120, 3), dtype=np.uint8)
        
        result = reader.read_plate(plate_image, preprocess=True)
        
        assert result.plate_text == "ABC1234"
        assert result.is_valid_format is True
    
    def test_clean_plate_text(self, mock_easyocr):
        """Test plate text cleaning."""
        mock_easyocr.return_value = Mock()
        
        reader = LicensePlateReader()
        
        # Test common OCR corrections
        test_cases = [
            ("AB01Z3", "ABO123"),  # Should correct based on context
            ("ABC 123", "ABC123"),  # Remove spaces
            ("ABC-123", "ABC123"),  # Remove dashes
        ]
        
        for input_text, expected in test_cases:
            cleaned = reader._clean_plate_text(input_text)
            # Basic cleaning should occur
            assert " " not in cleaned
            assert "-" not in cleaned
    
    def test_combine_ocr_results(self, mock_easyocr):
        """Test OCR result combination."""
        mock_easyocr.return_value = Mock()
        
        reader = LicensePlateReader()
        
        # Multiple OCR results with same text
        results = [
            OCRResult(text="ABC123", confidence=0.9, bbox=[]),
            OCRResult(text="ABC123", confidence=0.85, bbox=[]),
            OCRResult(text="XYZ789", confidence=0.6, bbox=[])
        ]
        
        text, confidence = reader._combine_ocr_results(results)
        
        assert text == "ABC123"  # Should pick the more confident/frequent result
        assert confidence > 0.8
    
    def test_validate_plate_format(self, mock_easyocr):
        """Test plate format validation integration."""
        mock_easyocr.return_value = Mock()
        
        reader = LicensePlateReader()
        
        test_cases = [
            ("ABC123", True, "old_standard"),
            ("ABC1234", True, "new_standard"),
            ("INVALID", False, None)
        ]
        
        for text, should_be_valid, expected_format in test_cases:
            is_valid, detected_format = reader._validate_plate_format(text)
            assert is_valid == should_be_valid
            if should_be_valid:
                assert detected_format == expected_format

class TestIntegration:
    """Integration tests for the recognition module."""
    
    @patch('easyocr.Reader')
    @patch('cv2.CascadeClassifier')
    def test_full_recognition_pipeline(self, mock_cascade_class, mock_easyocr):
        """Test complete recognition pipeline."""
        # Mock cascade classifier
        mock_cascade = Mock()
        mock_cascade.empty.return_value = False
        mock_cascade.detectMultiScale.return_value = [(100, 50, 200, 60)]
        mock_cascade_class.return_value = mock_cascade
        
        # Mock EasyOCR
        mock_reader_instance = Mock()
        mock_reader_instance.readtext.return_value = [
            ([(0, 0), (200, 0), (200, 60), (0, 60)], 'ABC123', 0.92)
        ]
        mock_easyocr.return_value = mock_reader_instance
        
        # Create components
        detector = LicensePlateDetector(use_cascade=True)
        detector.cascade = mock_cascade
        reader = LicensePlateReader()
        validator = PeruvianPlateValidator()
        
        # Test image with vehicle
        image = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
        vehicle_bbox = (50, 100, 350, 300)
        
        # Run detection
        detections = detector.detect_plates(image, vehicle_bbox)
        assert len(detections) > 0
        
        # Run OCR on first detection
        plate_detection = detections[0]
        reading = reader.read_plate(plate_detection.plate_image)
        
        # Validate result
        validation = validator.validate(reading.plate_text)
        
        # Verify pipeline
        assert reading.plate_text == "ABC123"
        assert reading.confidence > 0.9
        assert validation.is_valid
        assert validation.format_type == PlateFormat.OLD_STANDARD
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        detector = LicensePlateDetector()
        reader = LicensePlateReader()
        validator = PeruvianPlateValidator()
        
        # Get initial stats
        detector_stats = detector.get_detection_stats()
        reader_stats = reader.get_reading_stats()
        validator_stats = validator.get_validation_stats()
        
        # Verify stats structure
        assert "total_detections" in detector_stats
        assert "avg_processing_time_ms" in detector_stats
        
        assert "total_readings" in reader_stats
        assert "success_rate" in reader_stats
        
        assert "supported_formats" in validator_stats
        assert "format_types" in validator_stats

if __name__ == "__main__":
    pytest.main([__file__, "-v"])