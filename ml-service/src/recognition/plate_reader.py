"""
License Plate Reader using EasyOCR.

This module reads text from license plate images with 
optimized preprocessing and Peru-specific formatting.
"""

import logging
import time
import re
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2
from dataclasses import dataclass
import easyocr

from ..config import get_ml_settings

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """OCR reading result for a license plate."""
    text: str
    confidence: float
    bbox: List[Tuple[int, int]]  # List of corner points
    preprocessed_image: Optional[np.ndarray] = None

@dataclass
class PlateReading:
    """Complete license plate reading result."""
    plate_text: str
    confidence: float
    raw_ocr_results: List[OCRResult]
    is_valid_format: bool
    detected_format: Optional[str] = None
    processing_time_ms: float = 0.0

class LicensePlateReader:
    """
    License plate reader using EasyOCR with Peru-specific optimizations.
    
    Features:
    - High-accuracy text recognition with EasyOCR
    - Peru license plate format validation
    - Image preprocessing optimization
    - Multiple reading strategies
    - Performance monitoring
    """
    
    def __init__(self, languages: List[str] = None, gpu: bool = None):
        """
        Initialize license plate reader.
        
        Args:
            languages: List of languages for OCR (default: ['en'])
            gpu: Whether to use GPU acceleration (auto-detect if None)
        """
        self.settings = get_ml_settings()
        
        if languages is None:
            languages = ['en']  # English for alphanumeric plates
        
        if gpu is None:
            gpu = self.settings.gpu_enabled
        
        self.languages = languages
        self.gpu = gpu
        
        # Performance metrics
        self.total_processing_time = 0.0
        self.total_readings = 0
        self.successful_readings = 0
        
        # Initialize EasyOCR
        self._initialize_ocr()
        
        logger.info(f"LicensePlateReader initialized with languages: {languages}, GPU: {gpu}")
    
    def _initialize_ocr(self):
        """Initialize EasyOCR reader."""
        try:
            self.reader = easyocr.Reader(
                self.languages, 
                gpu=self.gpu,
                verbose=False,
                download_enabled=True
            )
            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            self.reader = None
    
    def read_plate(self, plate_image: np.ndarray, preprocess: bool = True) -> PlateReading:
        """
        Read text from license plate image.
        
        Args:
            plate_image: License plate image
            preprocess: Whether to apply preprocessing
            
        Returns:
            PlateReading with text and validation results
        """
        start_time = time.time()
        
        if self.reader is None:
            return PlateReading(
                plate_text="",
                confidence=0.0,
                raw_ocr_results=[],
                is_valid_format=False,
                processing_time_ms=0.0
            )
        
        # Preprocess image if requested
        processed_image = plate_image
        if preprocess:
            processed_image = self._preprocess_plate_image(plate_image)
        
        # Try multiple reading strategies
        reading_results = []
        
        # Strategy 1: Direct reading
        direct_result = self._read_with_easyocr(processed_image)
        if direct_result:
            reading_results.extend(direct_result)
        
        # Strategy 2: Enhanced preprocessing
        if not reading_results or max(r.confidence for r in reading_results) < 0.7:
            enhanced_image = self._enhanced_preprocessing(plate_image)
            enhanced_result = self._read_with_easyocr(enhanced_image)
            if enhanced_result:
                reading_results.extend(enhanced_result)
        
        # Strategy 3: Multiple scales
        if not reading_results or max(r.confidence for r in reading_results) < 0.8:
            for scale in [1.5, 2.0, 0.8]:
                scaled_image = self._scale_image(processed_image, scale)
                scaled_result = self._read_with_easyocr(scaled_image)
                if scaled_result:
                    reading_results.extend(scaled_result)
        
        # Process and combine results
        final_text, final_confidence = self._combine_ocr_results(reading_results)
        
        # Validate format
        is_valid, detected_format = self._validate_plate_format(final_text)
        
        # Clean up text
        cleaned_text = self._clean_plate_text(final_text)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Update metrics
        self.total_processing_time += processing_time / 1000
        self.total_readings += 1
        if is_valid:
            self.successful_readings += 1
        
        result = PlateReading(
            plate_text=cleaned_text,
            confidence=final_confidence,
            raw_ocr_results=reading_results,
            is_valid_format=is_valid,
            detected_format=detected_format,
            processing_time_ms=processing_time
        )
        
        logger.debug(f"Plate reading: '{cleaned_text}' (confidence: {final_confidence:.2f}, "
                    f"valid: {is_valid}, time: {processing_time:.1f}ms)")
        
        return result
    
    def _read_with_easyocr(self, image: np.ndarray) -> List[OCRResult]:
        """Read text using EasyOCR."""
        try:
            # EasyOCR expects RGB image
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif len(image.shape) == 2:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                rgb_image = image
            
            # Run OCR
            results = self.reader.readtext(
                rgb_image,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',  # Only alphanumeric
                width_ths=0.7,
                height_ths=0.7,
                paragraph=False,
                detail=1
            )
            
            ocr_results = []
            for bbox, text, confidence in results:
                # Filter low confidence results
                if confidence > 0.3:
                    ocr_results.append(OCRResult(
                        text=text.strip(),
                        confidence=confidence,
                        bbox=bbox,
                        preprocessed_image=image
                    ))
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"EasyOCR reading failed: {e}")
            return []
    
    def _preprocess_plate_image(self, image: np.ndarray) -> np.ndarray:
        """Standard preprocessing for plate images."""
        if image.size == 0:
            return image
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Resize to standard height
        target_height = 80
        if gray.shape[0] != target_height:
            width = int(gray.shape[1] * target_height / gray.shape[0])
            gray = cv2.resize(gray, (width, target_height))
        
        # Apply CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (1, 1), 0)
        
        # Sharpen the image
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(blurred, -1, kernel)
        
        return sharpened
    
    def _enhanced_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Enhanced preprocessing for difficult cases."""
        if image.size == 0:
            return image
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Resize to larger size for better recognition
        target_height = 120
        width = int(gray.shape[1] * target_height / gray.shape[0])
        resized = cv2.resize(gray, (width, target_height))
        
        # Bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(resized, 9, 75, 75)
        
        # Adaptive threshold
        adaptive = cv2.adaptiveThreshold(
            filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)
        
        # Invert if background is dark
        if np.mean(cleaned) < 127:
            cleaned = cv2.bitwise_not(cleaned)
        
        return cleaned
    
    def _scale_image(self, image: np.ndarray, scale: float) -> np.ndarray:
        """Scale image by given factor."""
        if image.size == 0:
            return image
        
        height, width = image.shape[:2]
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(image, (new_width, new_height))
    
    def _combine_ocr_results(self, results: List[OCRResult]) -> Tuple[str, float]:
        """Combine multiple OCR results into best reading."""
        if not results:
            return "", 0.0
        
        # Group similar results
        text_groups = {}
        for result in results:
            text = result.text.upper().replace(' ', '')
            if text not in text_groups:
                text_groups[text] = []
            text_groups[text].append(result)
        
        # Find best group (highest average confidence)
        best_text = ""
        best_confidence = 0.0
        
        for text, group in text_groups.items():
            if len(text) >= 6:  # Minimum length for valid plate
                avg_confidence = sum(r.confidence for r in group) / len(group)
                if avg_confidence > best_confidence:
                    best_confidence = avg_confidence
                    best_text = text
        
        # If no good groups, take highest individual confidence
        if not best_text:
            best_result = max(results, key=lambda r: r.confidence)
            best_text = best_result.text.upper().replace(' ', '')
            best_confidence = best_result.confidence
        
        return best_text, best_confidence
    
    def _validate_plate_format(self, text: str) -> Tuple[bool, Optional[str]]:
        """Validate if text matches Peruvian license plate formats."""
        if not text or len(text) < 6:
            return False, None
        
        # Clean text
        clean_text = text.upper().replace(' ', '').replace('-', '')
        
        # Peru formats:
        # Old format: ABC-123 (3 letters + 3 numbers)
        # New format: ABC-1234 (3 letters + 4 numbers)
        # Taxi format: T1A-123 (T + number + letter + 3 numbers)
        # Motorcycle: A1-123 (letter + number + 3 numbers)
        
        patterns = [
            (r'^[A-Z]{3}[0-9]{3}$', 'old_standard'),      # ABC123
            (r'^[A-Z]{3}[0-9]{4}$', 'new_standard'),      # ABC1234
            (r'^T[0-9][A-Z][0-9]{3}$', 'taxi'),           # T1A123
            (r'^[A-Z][0-9][0-9]{3}$', 'motorcycle'),      # A1123
            (r'^[A-Z]{2}[0-9]{4}$', 'commercial'),        # AB1234
            (r'^[0-9]{3}[A-Z]{3}$', 'old_reversed'),      # 123ABC (sometimes misread)
        ]
        
        for pattern, format_type in patterns:
            if re.match(pattern, clean_text):
                return True, format_type
        
        # Additional validation for common OCR errors
        if self._looks_like_plate(clean_text):
            return True, 'possible_valid'
        
        return False, None
    
    def _looks_like_plate(self, text: str) -> bool:
        """Check if text looks like a license plate despite format issues."""
        if len(text) < 6 or len(text) > 8:
            return False
        
        # Check for reasonable letter/number distribution
        letters = sum(1 for c in text if c.isalpha())
        numbers = sum(1 for c in text if c.isdigit())
        
        # Should have both letters and numbers
        if letters == 0 or numbers == 0:
            return False
        
        # Should be mostly letters and numbers
        alphanumeric = letters + numbers
        if alphanumeric / len(text) < 0.85:
            return False
        
        return True
    
    def _clean_plate_text(self, text: str) -> str:
        """Clean and format plate text."""
        if not text:
            return ""
        
        # Remove spaces and common OCR artifacts
        cleaned = text.upper().replace(' ', '').replace('-', '').replace('.', '')
        
        # Fix common OCR substitutions
        substitutions = {
            '0': 'O',  # Zero to O in letters
            'O': '0',  # O to zero in numbers (context dependent)
            '1': 'I',  # One to I in letters
            'I': '1',  # I to one in numbers (context dependent)
            '5': 'S',  # Five to S in letters
            'S': '5',  # S to five in numbers (context dependent)
            '8': 'B',  # Eight to B in letters
            'B': '8',  # B to eight in numbers (context dependent)
        }
        
        # Apply context-aware corrections
        result = ""
        for i, char in enumerate(cleaned):
            # Determine expected type based on common patterns
            if self._should_be_letter(cleaned, i):
                if char in '01589':
                    if char == '0':
                        result += 'O'
                    elif char == '1':
                        result += 'I'
                    elif char == '5':
                        result += 'S'
                    elif char == '8':
                        result += 'B'
                    else:
                        result += char
                else:
                    result += char
            elif self._should_be_number(cleaned, i):
                if char in 'OIS8B':
                    if char == 'O':
                        result += '0'
                    elif char == 'I':
                        result += '1'
                    elif char == 'S':
                        result += '5'
                    elif char == 'B':
                        result += '8'
                    else:
                        result += char
                else:
                    result += char
            else:
                result += char
        
        return result
    
    def _should_be_letter(self, text: str, position: int) -> bool:
        """Determine if character at position should be a letter."""
        # For standard formats, first 3 positions are usually letters
        if len(text) >= 6 and position < 3:
            return True
        return False
    
    def _should_be_number(self, text: str, position: int) -> bool:
        """Determine if character at position should be a number."""
        # For standard formats, last positions are usually numbers
        if len(text) >= 6 and position >= 3:
            return True
        return False
    
    def get_reading_stats(self) -> Dict[str, Any]:
        """Get reading performance statistics."""
        avg_time = self.total_processing_time / max(self.total_readings, 1)
        success_rate = self.successful_readings / max(self.total_readings, 1)
        
        return {
            "total_readings": self.total_readings,
            "successful_readings": self.successful_readings,
            "success_rate": success_rate,
            "avg_processing_time_ms": avg_time * 1000,
            "languages": self.languages,
            "gpu_enabled": self.gpu
        }
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.total_processing_time = 0.0
        self.total_readings = 0
        self.successful_readings = 0