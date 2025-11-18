"""
Enhanced Text Extraction with CLAHE preprocessing
Based on the improved repository code for robust plate recognition
"""
import cv2
import numpy as np
from typing import Tuple, Optional
from app.core import get_logger

logger = get_logger(__name__)


class TextExtraction:
    """
    Advanced text extraction with CLAHE preprocessing and exposure correction
    """
    
    def __init__(self):
        self.min_vertical_distance = 12
        
    def clahe(self, img: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        
        Args:
            img: Input BGR image
            
        Returns:
            Image with enhanced contrast
        """
        try:
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            clahe_img = clahe.apply(l)
            
            updated_lab_img = cv2.merge((clahe_img, a, b))
            CLAHE_img = cv2.cvtColor(updated_lab_img, cv2.COLOR_LAB2BGR)
            
            return CLAHE_img
        except Exception as e:
            logger.warning(f"CLAHE processing failed: {e}, returning original image")
            return img
    
    def exposure_level(self, hist: np.ndarray) -> str:
        """
        Determine if image is overexposed, underexposed, or properly exposed
        
        Args:
            hist: Histogram of the image
            
        Returns:
            Exposure level: "Overexposed", "Underexposed", or "Properly exposed"
        """
        hist = hist / np.sum(hist)
        percent_over = np.sum(hist[200:])
        percent_under = np.sum(hist[:50])
        
        if percent_over > 0.75:
            return "Overexposed"
        elif percent_under > 0.75:
            return "Underexposed"
        else:
            return "Properly exposed"
    
    def image_contrast(self, img: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast based on exposure level and contrast variance
        
        Args:
            img: Input BGR image
            
        Returns:
            Contrast-enhanced image
        """
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # Check exposure level
            exposure = self.exposure_level(hist)
            
            # Apply CLAHE if overexposed or underexposed
            if exposure in ["Overexposed", "Underexposed"]:
                logger.debug(f"Image is {exposure}, applying CLAHE")
                img = self.clahe(img)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Check contrast variance
            contrast = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # If low contrast, apply histogram equalization
            if contrast < 100:
                logger.debug(f"Low contrast detected ({contrast:.2f}), applying equalization")
                equalized = cv2.equalizeHist(gray)
                # Convert back to BGR
                img = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
            
            return img
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {e}, returning original image")
            return img
    
    def preprocess_for_ocr(self, plate_crop: np.ndarray) -> np.ndarray:
        """
        Complete preprocessing pipeline for OCR - ULTRA AGRESIVO
        
        Args:
            plate_crop: Cropped plate image
            
        Returns:
            Preprocessed image ready for OCR
        """
        try:
            # 1. Apply contrast enhancement (CLAHE + equalization)
            enhanced = self.image_contrast(plate_crop)
            
            # 2. Resize if too small (AGRESIVO: upscale a mínimo 100px altura)
            height, width = enhanced.shape[:2]
            if height < 100 or width < 300:
                scale_factor = max(100 / height, 300 / width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                enhanced = cv2.resize(enhanced, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                logger.debug(f"Upscaled plate from {width}x{height} to {new_width}x{new_height}")
            
            # 3. Convert to grayscale for better OCR
            gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
            
            # 4. Apply bilateral filter to reduce noise (más agresivo)
            gray = cv2.bilateralFilter(gray, 11, 90, 90)
            
            # 5. Apply adaptive threshold for better text separation
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
            
            # 6. Morphological operations to clean text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # 7. Sharpen the image
            kernel_sharp = np.array([[-1, -1, -1],
                                    [-1,  10, -1],
                                    [-1, -1, -1]])
            binary = cv2.filter2D(binary, -1, kernel_sharp)
            
            # Convert back to BGR for EasyOCR
            enhanced = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            
            return enhanced
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return plate_crop
    
    def validate_plate_format(self, text: str) -> Tuple[bool, str]:
        """
        Validate Peruvian license plate format - VERSIÓN FLEXIBLE
        
        Formatos válidos:
        - ABC-123 o ABC123 (3 letras - 3 números) ✅ MÁS COMÚN
        - AAA-123 o AAA123 (3 letras - 3 números)
        - A1B-234 o A1B234 (letra-número-letra - 3 números)
        - AB1-234 o AB1234 (2 letras-número - 3 números)
        - A12-345 (letra-2números - 3 números)
        
        Args:
            text: Extracted text from OCR
            
        Returns:
            Tuple of (is_valid, cleaned_text)
        """
        import re
        
        # Remove whitespace and convert to uppercase
        text = text.strip().upper().replace(" ", "").replace("_", "")
        
        # Si ya tiene guion en posición correcta, validar
        if '-' in text:
            parts = text.split('-')
            if len(parts) == 2:
                prefix, suffix = parts
                # Validar que prefix tiene 3 chars y suffix tiene 3 dígitos
                if len(prefix) == 3 and len(suffix) == 3 and suffix.isdigit():
                    # Prefix debe tener al menos 2 letras
                    letter_count = sum(1 for c in prefix if c.isalpha())
                    if letter_count >= 2:
                        logger.info(f"✅ Valid plate format (with dash): {text}")
                        return True, text
        
        # Check common Peruvian formats (SIN guion)
        patterns = [
            r'^[A-Z]{3}\d{3}$',        # ABC123 (MÁS COMÚN) ✅
            r'^[A-Z]\d[A-Z]\d{3}$',    # A1B234
            r'^[A-Z]{2}\d\d{3}$',      # AB1234
            r'^[A-Z]\d{2}\d{3}$',      # A12345
            r'^[A-Z]{4}\d{2}$',        # ABCD12 (formato antiguo)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                # Ensure format has dash (insertar en posición 3)
                if len(text) == 6:
                    text = text[:3] + '-' + text[3:]
                    logger.info(f"✅ Valid plate format: {text}")
                    return True, text
                elif len(text) == 5:
                    text = text[:2] + '-' + text[2:]
                    logger.info(f"✅ Valid plate format: {text}")
                    return True, text
        
        # VALIDACIÓN FLEXIBLE: Si tiene exactamente 6 caracteres alfanuméricos
        # con al menos 2 letras y 2 números, considerarlo válido
        if len(text) == 6:
            letter_count = sum(1 for c in text if c.isalpha())
            digit_count = sum(1 for c in text if c.isdigit())
            if letter_count >= 2 and digit_count >= 2:
                text = text[:3] + '-' + text[3:]
                logger.info(f"✅ Valid plate format (flexible): {text}")
                return True, text
        
        logger.debug(f"❌ Invalid plate format: {text}")
        return False, text
