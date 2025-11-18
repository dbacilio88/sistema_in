"""
Text Extraction using EasyOCR + TrOCR.

Advanced OCR pipeline combining EasyOCR for text detection and
Microsoft TrOCR for text recognition with enhanced preprocessing.
"""

import logging
import time
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2
from dataclasses import dataclass
from PIL import Image

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available")

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    TROCR_AVAILABLE = True
except ImportError:
    TROCR_AVAILABLE = False
    logging.warning("Transformers not available for TrOCR")

from ..config import get_ml_settings

logger = logging.getLogger(__name__)


@dataclass
class TextDetection:
    """Text detection result."""
    text: str
    confidence: float
    bbox: List[Tuple[int, int]]  # List of corner points
    method: str  # 'easyocr', 'trocr', 'combined'


@dataclass
class PlateText:
    """Complete plate text extraction result."""
    text: str
    confidence: float
    detections: List[TextDetection]
    preprocessed_image: Optional[np.ndarray] = None
    processing_time_ms: float = 0.0


class TextExtractor:
    """
    Advanced text extractor combining EasyOCR and TrOCR.
    
    Features:
    - Dual OCR pipeline (EasyOCR + TrOCR)
    - Advanced preprocessing with CLAHE
    - Multiple reading strategies
    - Character correction and validation
    - License plate format validation
    
    Pipeline:
    1. Image preprocessing (CLAHE, denoising, sharpening)
    2. Text detection with EasyOCR
    3. Text recognition with TrOCR (optional)
    4. Result fusion and validation
    5. Format-specific post-processing
    """
    
    def __init__(
        self,
        languages: List[str] = None,
        use_trocr: bool = True,
        gpu: bool = None,
        trocr_model: str = 'microsoft/trocr-base-printed'
    ):
        """
        Initialize text extractor.
        
        Args:
            languages: Languages for EasyOCR (default: ['en'])
            use_trocr: Whether to use TrOCR in addition to EasyOCR
            gpu: Whether to use GPU acceleration
            trocr_model: TrOCR model to use
        """
        if not EASYOCR_AVAILABLE:
            raise RuntimeError("EasyOCR not installed. Install with: pip install easyocr")
        
        self.settings = get_ml_settings()
        
        if languages is None:
            languages = ['en']
        
        if gpu is None:
            gpu = self.settings.gpu_enabled if hasattr(self.settings, 'gpu_enabled') else False
        
        self.languages = languages
        self.gpu = gpu
        self.use_trocr = use_trocr and TROCR_AVAILABLE
        self.trocr_model_name = trocr_model
        
        # OCR readers
        self.easyocr_reader = None
        self.trocr_processor = None
        self.trocr_model = None
        
        # Performance metrics
        self.total_processing_time = 0.0
        self.total_extractions = 0
        self.successful_extractions = 0
        
        self._initialize_ocr()
        
        logger.info(
            f"TextExtractor initialized - EasyOCR: {languages}, "
            f"TrOCR: {self.use_trocr}, GPU: {gpu}"
        )
    
    def _initialize_ocr(self):
        """Initialize OCR models."""
        # Initialize EasyOCR
        try:
            logger.info("Loading EasyOCR...")
            self.easyocr_reader = easyocr.Reader(
                self.languages,
                gpu=self.gpu,
                verbose=False,
                download_enabled=True
            )
            logger.info("EasyOCR loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load EasyOCR: {e}")
            raise
        
        # Initialize TrOCR
        if self.use_trocr:
            try:
                logger.info(f"Loading TrOCR model: {self.trocr_model_name}...")
                self.trocr_processor = TrOCRProcessor.from_pretrained(self.trocr_model_name)
                self.trocr_model = VisionEncoderDecoderModel.from_pretrained(self.trocr_model_name)
                
                if self.gpu and torch.cuda.is_available():
                    self.trocr_model = self.trocr_model.to('cuda')
                
                logger.info("TrOCR loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load TrOCR: {e}")
                self.use_trocr = False
    
    def extract(
        self,
        plate_image: np.ndarray,
        apply_preprocessing: bool = True,
        use_multiple_strategies: bool = True
    ) -> PlateText:
        """
        Extract text from plate image.
        
        Args:
            plate_image: License plate image
            apply_preprocessing: Whether to apply preprocessing
            use_multiple_strategies: Whether to try multiple extraction strategies
            
        Returns:
            PlateText with extracted text and confidence
        """
        start_time = time.time()
        
        if plate_image.size == 0:
            return PlateText(text='', confidence=0.0, detections=[], processing_time_ms=0.0)
        
        preprocessed = None
        all_detections = []
        
        try:
            # Preprocess image
            if apply_preprocessing:
                preprocessed = self._preprocess_image(plate_image)
            else:
                preprocessed = plate_image
            
            # Strategy 1: EasyOCR on preprocessed image
            easyocr_detections = self._extract_with_easyocr(preprocessed)
            all_detections.extend(easyocr_detections)
            
            # Strategy 2: Try multiple preprocessing variations
            if use_multiple_strategies and len(all_detections) == 0:
                variations = self._create_image_variations(plate_image)
                for var_img in variations:
                    var_detections = self._extract_with_easyocr(var_img)
                    all_detections.extend(var_detections)
                    if var_detections:
                        break
            
            # Strategy 3: TrOCR for additional validation
            if self.use_trocr and preprocessed is not None:
                trocr_result = self._extract_with_trocr(preprocessed)
                if trocr_result:
                    all_detections.append(trocr_result)
            
            # Select best result
            if all_detections:
                best_detection = max(all_detections, key=lambda d: d.confidence)
                final_text = self._post_process_text(best_detection.text)
                final_confidence = best_detection.confidence
                self.successful_extractions += 1
            else:
                final_text = ''
                final_confidence = 0.0
            
            # Update metrics
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            self.total_extractions += 1
            
            return PlateText(
                text=final_text,
                confidence=final_confidence,
                detections=all_detections,
                preprocessed_image=preprocessed,
                processing_time_ms=processing_time * 1000
            )
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return PlateText(text='', confidence=0.0, detections=[], processing_time_ms=0.0)
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Advanced preprocessing optimized for WHITE Peruvian license plates.
        
        Peruvian plates are WHITE background with BLACK text (not yellow).
        Format: ABC-123 or ABC 123
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Resize for better OCR (min height 64px)
        if gray.shape[0] < 64:
            scale = 64 / gray.shape[0]
            new_width = int(gray.shape[1] * scale)
            gray = cv2.resize(gray, (new_width, 64))
        
        # For WHITE plates with BLACK text, we want to enhance contrast
        # CLAHE for contrast enhancement - more aggressive for white plates
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoising to remove noise from white background
        denoised = cv2.fastNlMeansDenoising(enhanced, h=15)
        
        # Sharpening to make BLACK text on WHITE background clearer
        kernel_sharpening = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ])
        sharpened = cv2.filter2D(denoised, -1, kernel_sharpening)
        
        # Additional thresholding for white plates
        # This helps separate BLACK text from WHITE background
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _create_image_variations(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Create multiple preprocessed variations for robust OCR.
        
        Args:
            image: Input image
            
        Returns:
            List of preprocessed variations
        """
        variations = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Variation 1: Adaptive thresholding
        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        variations.append(adaptive)
        
        # Variation 2: Otsu's thresholding
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variations.append(otsu)
        
        # Variation 3: Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        variations.append(morph)
        
        return variations
    
    def _extract_with_easyocr(self, image: np.ndarray) -> List[TextDetection]:
        """Extract text using EasyOCR."""
        detections = []
        
        try:
            # Convert to RGB for EasyOCR
            if len(image.shape) == 2:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            # Run EasyOCR
            results = self.easyocr_reader.readtext(
                rgb_image,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                detail=1,
                paragraph=False,
                min_size=10,
                text_threshold=0.3,
                low_text=0.2,
                link_threshold=0.2,
                canvas_size=2560,
                mag_ratio=1.5
            )
            
            for bbox, text, confidence in results:
                if confidence > 0.2:  # Filter low confidence
                    detection = TextDetection(
                        text=text.strip().upper(),
                        confidence=confidence,
                        bbox=bbox,
                        method='easyocr'
                    )
                    detections.append(detection)
        
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {e}")
        
        return detections
    
    def _extract_with_trocr(self, image: np.ndarray) -> Optional[TextDetection]:
        """Extract text using TrOCR."""
        if not self.use_trocr:
            return None
        
        try:
            # Convert to PIL Image
            if len(image.shape) == 2:
                pil_image = Image.fromarray(image).convert('RGB')
            else:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Process with TrOCR
            pixel_values = self.trocr_processor(pil_image, return_tensors='pt').pixel_values
            
            if self.gpu and torch.cuda.is_available():
                pixel_values = pixel_values.to('cuda')
            
            # Generate text
            generated_ids = self.trocr_model.generate(pixel_values)
            generated_text = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # TrOCR doesn't provide confidence, estimate based on length
            confidence = min(0.85, 0.5 + len(generated_text) * 0.05)
            
            return TextDetection(
                text=generated_text.strip().upper(),
                confidence=confidence,
                bbox=[],
                method='trocr'
            )
        
        except Exception as e:
            logger.error(f"TrOCR extraction failed: {e}")
            return None
    
    def _post_process_text(self, text: str) -> str:
        """
        Post-process extracted text for Peruvian license plates.
        
        Peruvian format: ABC-123 or ABC 123
        - 3 letters followed by 3 numbers
        - Separator can be hyphen or space
        - Normalize to ABC-123 format
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned and normalized text in ABC-123 format
        """
        # Remove all special characters except hyphen and space
        text = ''.join(c for c in text if c.isalnum() or c in ['-', ' '])
        
        # Convert to uppercase
        text = text.upper()
        
        # Common character corrections for license plates
        corrections = {
            'O': '0',  # O to 0 in numeric positions
            'I': '1',  # I to 1 in numeric positions
            'Z': '2',  # Z to 2 in numeric contexts
            'S': '5',  # S to 5 in numeric contexts
            'B': '8',  # B to 8 in numeric contexts
            'G': '6',  # G to 6 in numeric contexts
        }
        
        # Try to identify Peruvian format: ABC-123 or ABC 123
        # Remove any existing separators
        clean_text = text.replace('-', '').replace(' ', '')
        
        # Apply corrections based on position
        if len(clean_text) >= 6:
            # First 3 should be letters, last 3 should be numbers
            letters = clean_text[:3]
            numbers = clean_text[3:6]
            
            # Correct letters (remove numbers that look like letters)
            # A-Z only
            letters = ''.join(c for c in letters if c.isalpha())
            
            # Correct numbers (convert letter-like characters to numbers)
            corrected_numbers = ''
            for c in numbers:
                if c in corrections:
                    corrected_numbers += corrections[c]
                elif c.isdigit():
                    corrected_numbers += c
                # Skip non-digit, non-correctable characters
            
            # Reconstruct in standard ABC-123 format
            if len(letters) == 3 and len(corrected_numbers) == 3:
                text = f"{letters}-{corrected_numbers}"
            else:
                # If format doesn't match, return cleaned text
                text = clean_text
        
        return text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extractor statistics."""
        avg_time = self.total_processing_time / self.total_extractions if self.total_extractions > 0 else 0
        success_rate = self.successful_extractions / self.total_extractions if self.total_extractions > 0 else 0
        
        return {
            'total_extractions': self.total_extractions,
            'successful_extractions': self.successful_extractions,
            'success_rate': success_rate,
            'avg_processing_time_ms': avg_time * 1000,
            'using_trocr': self.use_trocr
        }
