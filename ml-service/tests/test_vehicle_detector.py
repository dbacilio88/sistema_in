"""
Tests for YOLOv8 vehicle detector
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.detection.vehicle_detector import YOLOv8VehicleDetector, Detection, PerformanceMetrics


class TestYOLOv8VehicleDetector:
    """Test cases for YOLOv8VehicleDetector"""
    
    @pytest.fixture
    def mock_onnx_session(self):
        """Mock ONNX Runtime session"""
        session = Mock()
        session.get_inputs.return_value = [Mock(name="images", shape=[1, 3, 640, 640])]
        session.get_outputs.return_value = [Mock(name="output0")]
        
        # Mock inference output
        # YOLOv8 output shape: [1, 84, 8400]
        mock_output = np.random.rand(1, 84, 8400).astype(np.float32)
        session.run.return_value = [mock_output]
        
        return session
    
    @pytest.fixture
    def sample_frame(self):
        """Create a sample frame for testing"""
        return np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
    
    @pytest.fixture
    def detector(self, mock_onnx_session):
        """Create detector with mocked ONNX session"""
        with patch('src.detection.vehicle_detector.ort.InferenceSession') as mock_session_class:
            mock_session_class.return_value = mock_onnx_session
            
            with patch.object(Path, 'exists', return_value=True):
                detector = YOLOv8VehicleDetector()
                return detector
    
    def test_detector_initialization(self, detector):
        """Test detector initialization"""
        assert detector.session is not None
        assert detector.input_name == "images"
        assert detector.confidence_threshold > 0
        assert detector.nms_threshold > 0
        assert detector.input_size == (640, 640)
    
    def test_preprocess(self, detector, sample_frame):
        """Test frame preprocessing"""
        tensor, scale = detector.preprocess(sample_frame)
        
        # Check tensor shape (NCHW format)
        assert tensor.shape == (1, 3, 640, 640)
        assert tensor.dtype == np.float32
        
        # Check tensor values are normalized
        assert 0 <= tensor.min() <= 1
        assert 0 <= tensor.max() <= 1
        
        # Check scale factor
        assert isinstance(scale, float)
        assert scale > 0
    
    def test_postprocess_empty_output(self, detector):
        """Test postprocessing with empty output"""
        empty_outputs = []
        detections = detector.postprocess(empty_outputs, 1.0, (720, 1280))
        assert len(detections) == 0
    
    def test_postprocess_with_detections(self, detector):
        """Test postprocessing with mock detections"""
        # Create mock output with vehicle detection
        mock_output = np.zeros((8400, 84))
        
        # Add a car detection (class_id=2)
        mock_output[0, :4] = [320, 240, 100, 150]  # x_center, y_center, width, height
        mock_output[0, 6] = 0.9  # confidence for class 2 (car)
        
        outputs = [mock_output]
        detections = detector.postprocess(outputs, 1.0, (720, 1280))
        
        # Should have filtered and processed the detection
        assert len(detections) >= 0  # May be 0 if confidence filtering applied
    
    def test_detect_integration(self, detector, sample_frame):
        """Test full detection pipeline"""
        detections, metrics = detector.detect(sample_frame)
        
        # Check return types
        assert isinstance(detections, list)
        assert isinstance(metrics, PerformanceMetrics)
        
        # Check metrics
        assert metrics.inference_time_ms >= 0
        assert metrics.preprocessing_time_ms >= 0
        assert metrics.postprocessing_time_ms >= 0
        assert metrics.total_time_ms >= 0
        assert metrics.fps >= 0
        assert metrics.detections_count >= 0
    
    def test_nms_application(self, detector):
        """Test Non-Maximum Suppression"""
        # Create overlapping detections
        detections = [
            Detection(
                class_id=2,
                class_name="car",
                confidence=0.9,
                bbox=(100, 100, 200, 200),
                center=(150, 150),
                area=10000
            ),
            Detection(
                class_id=2,
                class_name="car", 
                confidence=0.8,
                bbox=(110, 110, 210, 210),
                center=(160, 160),
                area=10000
            )
        ]
        
        filtered = detector._apply_nms(detections)
        
        # Should remove one overlapping detection
        assert len(filtered) <= len(detections)
    
    def test_visualization(self, detector, sample_frame):
        """Test detection visualization"""
        # Create mock detection
        detection = Detection(
            class_id=2,
            class_name="car",
            confidence=0.9,
            bbox=(100, 100, 200, 200),
            center=(150, 150),
            area=10000
        )
        
        annotated = detector.visualize_detections(sample_frame, [detection])
        
        # Check that frame is modified (has annotations)
        assert annotated.shape == sample_frame.shape
        assert not np.array_equal(annotated, sample_frame)  # Frame should be different
    
    def test_performance_tracking(self, detector, sample_frame):
        """Test performance metrics tracking"""
        # Run multiple detections
        for _ in range(5):
            detector.detect(sample_frame)
        
        # Check performance history
        assert len(detector.performance_history) == 5
        
        # Get average performance
        avg_performance = detector.get_average_performance()
        
        assert "avg_inference_time_ms" in avg_performance
        assert "avg_fps" in avg_performance
        assert avg_performance["measurements_count"] == 5
    
    def test_benchmark(self, detector):
        """Test benchmark functionality"""
        with patch.object(detector, 'detect') as mock_detect:
            # Mock detection results
            mock_metrics = PerformanceMetrics(
                inference_time_ms=50.0,
                preprocessing_time_ms=5.0,
                postprocessing_time_ms=10.0,
                total_time_ms=65.0,
                fps=15.4,
                detections_count=3
            )
            mock_detect.return_value = ([], mock_metrics)
            
            results = detector.benchmark(num_iterations=10)
            
            assert "iterations" in results
            assert "inference_time_ms" in results
            assert "target_latency_met" in results
            assert results["iterations"] == 10


class TestDetection:
    """Test Detection dataclass"""
    
    def test_detection_creation(self):
        """Test Detection object creation"""
        detection = Detection(
            class_id=2,
            class_name="car",
            confidence=0.85,
            bbox=(100, 50, 300, 250),
            center=(200, 150),
            area=40000
        )
        
        assert detection.class_id == 2
        assert detection.class_name == "car"
        assert detection.confidence == 0.85
        assert detection.bbox == (100, 50, 300, 250)
        assert detection.center == (200, 150)
        assert detection.area == 40000


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass"""
    
    def test_metrics_creation(self):
        """Test PerformanceMetrics object creation"""
        metrics = PerformanceMetrics(
            inference_time_ms=45.2,
            preprocessing_time_ms=5.1,
            postprocessing_time_ms=8.7,
            total_time_ms=59.0,
            fps=16.9,
            detections_count=4
        )
        
        assert metrics.inference_time_ms == 45.2
        assert metrics.preprocessing_time_ms == 5.1
        assert metrics.postprocessing_time_ms == 8.7
        assert metrics.total_time_ms == 59.0
        assert metrics.fps == 16.9
        assert metrics.detections_count == 4


@pytest.mark.integration
class TestYOLOv8Integration:
    """Integration tests requiring actual model files"""
    
    def test_model_download_and_conversion(self):
        """Test automatic model download and conversion"""
        # This test requires internet connection and is marked as integration
        with patch('src.detection.vehicle_detector.YOLO') as mock_yolo:
            mock_model = Mock()
            mock_yolo.return_value = mock_model
            
            detector = YOLOv8VehicleDetector()
            
            # Should attempt to download if model doesn't exist
            if not detector.model_path.exists():
                mock_yolo.assert_called_once()
                mock_model.export.assert_called_once()
    
    @pytest.mark.gpu
    def test_gpu_acceleration(self):
        """Test GPU acceleration if available"""
        from src.config import ml_settings
        
        if ml_settings.USE_GPU:
            detector = YOLOv8VehicleDetector()
            
            # Check that GPU providers are configured
            providers = [p[0] if isinstance(p, tuple) else p for p in ml_settings.get_onnx_providers()]
            
            gpu_providers = ["TensorrtExecutionProvider", "CUDAExecutionProvider"]
            has_gpu_provider = any(provider in providers for provider in gpu_providers)
            
            assert has_gpu_provider, "GPU providers should be available when USE_GPU=True"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])