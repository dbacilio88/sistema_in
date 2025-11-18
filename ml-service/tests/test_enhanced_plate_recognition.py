"""
Test suite for enhanced plate recognition pipeline.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock

# Import components
from ml_service.src.recognition.vehicle_detection import VehicleDetector, VehicleDetection
from ml_service.src.recognition.plate_segmentation import PlateSegmenter, PlateSegmentation
from ml_service.src.recognition.text_extraction import TextExtractor, PlateText
from ml_service.src.recognition.plate_recognition_pipeline import PlateRecognitionPipeline


@pytest.fixture
def sample_image():
    """Create sample test image."""
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add some noise
    image = cv2.randn(image, (127, 127, 127), (30, 30, 30))
    return image


@pytest.fixture
def sample_plate_image():
    """Create sample plate image with text."""
    plate = np.ones((60, 200, 3), dtype=np.uint8) * 255
    cv2.putText(plate, "ABC-123", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    return plate


class TestVehicleDetector:
    """Test vehicle detection component."""
    
    @patch('ml_service.src.recognition.vehicle_detection.YOLO')
    def test_initialization(self, mock_yolo):
        """Test detector initialization."""
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        
        detector = VehicleDetector(confidence_threshold=0.5)
        
        assert detector is not None
        assert detector.confidence_threshold == 0.5
        assert detector.target_classes == [2, 3, 5, 7]
    
    @patch('ml_service.src.recognition.vehicle_detection.YOLO')
    def test_detect_vehicles(self, mock_yolo, sample_image):
        """Test vehicle detection."""
        # Mock YOLO results
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_boxes = MagicMock()
        
        # Simulate detection
        mock_box = MagicMock()
        mock_box.xyxy = [np.array([100, 100, 300, 250])]
        mock_box.conf = [np.array([0.85])]
        mock_box.cls = [np.array([2])]  # car
        
        mock_boxes.__len__ = lambda x: 1
        mock_boxes.__iter__ = lambda x: iter([mock_box])
        mock_result.boxes = mock_boxes
        mock_model.predict.return_value = [mock_result]
        mock_yolo.return_value = mock_model
        
        detector = VehicleDetector()
        detections, _ = detector.detect(sample_image)
        
        assert len(detections) == 1
        assert detections[0].vehicle_class == 'car'
        assert detections[0].confidence == 0.85
    
    @patch('ml_service.src.recognition.vehicle_detection.YOLO')
    def test_batch_detection(self, mock_yolo, sample_image):
        """Test batch vehicle detection."""
        mock_model = MagicMock()
        mock_model.predict.return_value = []
        mock_yolo.return_value = mock_model
        
        detector = VehicleDetector()
        images = [sample_image, sample_image, sample_image]
        results = detector.detect_batch(images)
        
        assert len(results) == 3
        assert isinstance(results, list)


class TestPlateSegmenter:
    """Test plate segmentation component."""
    
    @patch('ml_service.src.recognition.plate_segmentation.YOLO')
    def test_initialization(self, mock_yolo):
        """Test segmenter initialization."""
        segmenter = PlateSegmenter(use_cascade_fallback=True)
        
        assert segmenter is not None
        assert segmenter.confidence_threshold == 0.4
    
    @patch('ml_service.src.recognition.plate_segmentation.YOLO')
    @patch('cv2.CascadeClassifier')
    def test_segment_with_cascade(self, mock_cascade, mock_yolo, sample_image):
        """Test plate segmentation with cascade."""
        # Mock cascade detection
        mock_cascade_instance = MagicMock()
        mock_cascade_instance.detectMultiScale.return_value = np.array([
            [150, 120, 100, 30]  # x, y, w, h
        ])
        mock_cascade_instance.empty.return_value = False
        mock_cascade.return_value = mock_cascade_instance
        
        segmenter = PlateSegmenter(model_path=None, use_cascade_fallback=True)
        vehicle_bbox = (100, 100, 400, 300)
        
        segmentations = segmenter.segment(sample_image, vehicle_bbox)
        
        assert len(segmentations) >= 0
    
    @patch('ml_service.src.recognition.plate_segmentation.YOLO')
    def test_preprocess_plate(self, mock_yolo, sample_plate_image):
        """Test plate preprocessing."""
        segmenter = PlateSegmenter()
        processed = segmenter.preprocess_plate(sample_plate_image)
        
        assert processed is not None
        assert processed.shape[0] == 64  # Height should be standardized


class TestTextExtractor:
    """Test text extraction component."""
    
    @patch('easyocr.Reader')
    def test_initialization(self, mock_reader):
        """Test extractor initialization."""
        mock_reader_instance = MagicMock()
        mock_reader.return_value = mock_reader_instance
        
        extractor = TextExtractor(use_trocr=False)
        
        assert extractor is not None
        assert extractor.languages == ['en']
    
    @patch('easyocr.Reader')
    def test_extract_text(self, mock_reader, sample_plate_image):
        """Test text extraction."""
        # Mock EasyOCR results
        mock_reader_instance = MagicMock()
        mock_reader_instance.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 30], [0, 30]], 'ABC123', 0.92)
        ]
        mock_reader.return_value = mock_reader_instance
        
        extractor = TextExtractor(use_trocr=False)
        result = extractor.extract(sample_plate_image)
        
        assert result.text == 'ABC123'
        assert result.confidence > 0.9
    
    @patch('easyocr.Reader')
    def test_preprocessing(self, mock_reader, sample_plate_image):
        """Test image preprocessing."""
        mock_reader_instance = MagicMock()
        mock_reader.return_value = mock_reader_instance
        
        extractor = TextExtractor(use_trocr=False)
        preprocessed = extractor._preprocess_image(sample_plate_image)
        
        assert preprocessed is not None
        assert len(preprocessed.shape) == 2  # Should be grayscale
    
    @patch('easyocr.Reader')
    def test_image_variations(self, mock_reader, sample_plate_image):
        """Test creation of image variations."""
        mock_reader_instance = MagicMock()
        mock_reader.return_value = mock_reader_instance
        
        extractor = TextExtractor(use_trocr=False)
        variations = extractor._create_image_variations(sample_plate_image)
        
        assert len(variations) == 3
        assert all(isinstance(v, np.ndarray) for v in variations)


class TestPlateRecognitionPipeline:
    """Test complete pipeline integration."""
    
    @patch('ml_service.src.recognition.vehicle_detection.YOLO')
    @patch('easyocr.Reader')
    def test_pipeline_initialization(self, mock_reader, mock_yolo):
        """Test pipeline initialization."""
        mock_yolo_instance = MagicMock()
        mock_yolo.return_value = mock_yolo_instance
        
        mock_reader_instance = MagicMock()
        mock_reader.return_value = mock_reader_instance
        
        pipeline = PlateRecognitionPipeline(use_trocr=False)
        
        assert pipeline is not None
        assert pipeline.vehicle_detector is not None
        assert pipeline.vehicle_tracker is not None
        assert pipeline.plate_segmenter is not None
        assert pipeline.text_extractor is not None
    
    @patch('ml_service.src.recognition.vehicle_detection.YOLO')
    @patch('easyocr.Reader')
    @patch('cv2.CascadeClassifier')
    def test_process_frame(self, mock_cascade, mock_reader, mock_yolo, sample_image):
        """Test single frame processing."""
        # Mock vehicle detection
        mock_yolo_instance = MagicMock()
        mock_result = MagicMock()
        mock_boxes = MagicMock()
        
        mock_box = MagicMock()
        mock_box.xyxy = [np.array([100, 100, 300, 250])]
        mock_box.conf = [np.array([0.85])]
        mock_box.cls = [np.array([2])]
        
        mock_boxes.__len__ = lambda x: 1
        mock_boxes.__iter__ = lambda x: iter([mock_box])
        mock_result.boxes = mock_boxes
        mock_yolo_instance.predict.return_value = [mock_result]
        mock_yolo.return_value = mock_yolo_instance
        
        # Mock OCR
        mock_reader_instance = MagicMock()
        mock_reader_instance.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 30], [0, 30]], 'ABC123', 0.92)
        ]
        mock_reader.return_value = mock_reader_instance
        
        # Mock cascade
        mock_cascade_instance = MagicMock()
        mock_cascade_instance.detectMultiScale.return_value = np.array([[150, 120, 100, 30]])
        mock_cascade_instance.empty.return_value = False
        mock_cascade.return_value = mock_cascade_instance
        
        pipeline = PlateRecognitionPipeline(use_trocr=False)
        results = pipeline.process_frame(sample_image)
        
        assert isinstance(results, list)
    
    @patch('ml_service.src.recognition.vehicle_detection.YOLO')
    @patch('easyocr.Reader')
    def test_validate_plate_format(self, mock_reader, mock_yolo):
        """Test plate format validation."""
        mock_yolo_instance = MagicMock()
        mock_yolo.return_value = mock_yolo_instance
        
        mock_reader_instance = MagicMock()
        mock_reader.return_value = mock_reader_instance
        
        pipeline = PlateRecognitionPipeline(use_trocr=False)
        
        # Valid formats
        assert pipeline._validate_plate_format('ABC123')
        assert pipeline._validate_plate_format('ABC-123')
        assert pipeline._validate_plate_format('AB1234')
        assert pipeline._validate_plate_format('AB-1234')
        
        # Invalid formats
        assert not pipeline._validate_plate_format('A')
        assert not pipeline._validate_plate_format('AB')
    
    @patch('ml_service.src.recognition.vehicle_detection.YOLO')
    @patch('easyocr.Reader')
    def test_get_stats(self, mock_reader, mock_yolo):
        """Test statistics retrieval."""
        mock_yolo_instance = MagicMock()
        mock_yolo.return_value = mock_yolo_instance
        
        mock_reader_instance = MagicMock()
        mock_reader.return_value = mock_reader_instance
        
        pipeline = PlateRecognitionPipeline(use_trocr=False)
        stats = pipeline.get_stats()
        
        assert 'frames_processed' in stats
        assert 'total_vehicles_detected' in stats
        assert 'total_plates_recognized' in stats
        assert stats['frames_processed'] == 0


@pytest.mark.integration
class TestPipelineIntegration:
    """Integration tests for complete pipeline."""
    
    def test_end_to_end_detection(self):
        """Test complete end-to-end detection pipeline."""
        # This would require actual models and test video
        # Placeholder for integration test
        pass
    
    def test_video_processing(self):
        """Test video file processing."""
        # This would require test video file
        # Placeholder for integration test
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
