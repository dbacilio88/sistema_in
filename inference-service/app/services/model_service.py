"""
ML Models Service - Handles loading and inference with YOLOv8 and OCR
"""
import os
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import cv2
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core import get_logger, settings
from app.services.traffic_light_detector import SimpleTrafficLightDetector
from app.services.lane_detector import SimpleLaneDetector

logger = get_logger(__name__)


class ModelService:
    """Service for managing ML models (YOLO, OCR, Traffic Light, Lane Detection)"""
    
    def __init__(self):
        self.yolo_model = None
        self.ocr_reader = None
        self.traffic_light_detector = None
        self.lane_detector = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._initialized = False
        
    async def initialize(self):
        """Initialize and load all ML models"""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing ML models...")
            
            # Load YOLO model in thread pool to avoid blocking
            self.yolo_model = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._load_yolo_model
            )
            
            # Load OCR reader (optional - don't fail if it doesn't work)
            try:
                self.ocr_reader = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._load_ocr_reader
                )
                logger.info("OCR reader loaded successfully")
            except Exception as ocr_error:
                logger.warning(f"Failed to load OCR reader: {str(ocr_error)}")
                logger.warning("Continuing without OCR support")
                self.ocr_reader = None
            
            # Initialize traffic light detector (lightweight, no ML model needed)
            try:
                # Pass YOLO model to traffic light detector for object detection
                self.traffic_light_detector = SimpleTrafficLightDetector(
                    yolo_model=self.yolo_model,
                    confidence_threshold=0.5
                )
                logger.info("✅ Traffic light detector initialized with YOLO support")
            except Exception as tl_error:
                logger.warning(f"Failed to initialize traffic light detector: {str(tl_error)}")
                self.traffic_light_detector = None
            
            # Initialize lane detector (lightweight, uses Hough Transform)
            try:
                self.lane_detector = SimpleLaneDetector(
                    confidence_threshold=0.6
                )
                logger.info("✅ Lane detector initialized")
            except Exception as lane_error:
                logger.warning(f"Failed to initialize lane detector: {str(lane_error)}")
                self.lane_detector = None
            
            self._initialized = True
            logger.info("ML models initialized successfully (YOLO + Traffic Light + Lane Detection ready)")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {str(e)}")
            raise
    
    def _load_yolo_model(self):
        """Load YOLOv8 model (runs in thread pool)"""
        try:
            from ultralytics import YOLO
            
            model_path = settings.YOLO_MODEL_PATH
            
            # Check if model exists, if not download it
            if not os.path.exists(model_path):
                logger.info(f"YOLO model not found at {model_path}, downloading...")
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                # This will download the model to the models directory
                model = YOLO('yolov8n.pt')
                # Move the downloaded file to our models directory
                import shutil
                if os.path.exists('yolov8n.pt') and not os.path.exists(model_path):
                    shutil.move('yolov8n.pt', model_path)
                # Now load from the correct path
                model = YOLO(model_path)
            else:
                model = YOLO(model_path)
            
            logger.info(f"YOLO model loaded from {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            raise
    
    def _load_ocr_reader(self):
        """Load EasyOCR reader (runs in thread pool)"""
        try:
            import easyocr
            
            reader = easyocr.Reader(
                settings.OCR_LANGUAGES,
                gpu=settings.OCR_GPU
            )
            
            logger.info(f"OCR reader loaded for languages: {settings.OCR_LANGUAGES}")
            return reader
            
        except Exception as e:
            logger.error(f"Failed to load OCR reader: {str(e)}")
            raise
    
    async def detect_vehicles(
        self,
        frame: np.ndarray,
        confidence_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Detect vehicles in a frame using YOLO
        
        Args:
            frame: Input image as numpy array
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            List of detections with bbox, confidence, and class
        """
        if not self._initialized:
            await self.initialize()
        
        if confidence_threshold is None:
            confidence_threshold = settings.YOLO_CONFIDENCE_THRESHOLD
        
        try:
            # Run YOLO inference in thread pool
            results = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.yolo_model.predict(
                    frame,
                    conf=confidence_threshold,
                    iou=settings.YOLO_IOU_THRESHOLD,
                    verbose=False
                )
            )
            
            detections = []
            
            # YOLO vehicle classes (COCO dataset)
            # NOTA: Para pruebas, también detectamos personas (class=0)
            vehicle_classes = {
                0: 'person',      # 👤 Para pruebas y peatones
                1: 'bicycle',     # 🚲 Bicicletas
                2: 'car',         # 🚗 Autos
                3: 'motorcycle',  # 🏍️ Motos
                5: 'bus',         # 🚌 Buses
                7: 'truck'        # 🚚 Camiones
            }
            
            # Process results
            for result in results:
                boxes = result.boxes
                logger.info(f"🔍 YOLO detected {len(boxes)} objects total")
                
                vehicle_count = 0
                for idx, box in enumerate(boxes):
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Log cada objeto detectado
                    logger.info(f"📦 Object #{idx+1}: class={cls}, confidence={conf:.2f}")
                    
                    # Only process vehicle classes
                    if cls in vehicle_classes:
                        vehicle_count += 1
                        xyxy = box.xyxy[0].cpu().numpy()
                        
                        # Formato correcto: [x1, y1, x2, y2]
                        bbox = [float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])]
                        
                        detection = {
                            'type': 'vehicle',
                            'vehicle_type': vehicle_classes[cls],
                            'confidence': conf,
                            'bbox': bbox  # [x1, y1, x2, y2]
                        }
                        detections.append(detection)
                        
                        logger.info(
                            f"✅ Vehicle detected: {vehicle_classes[cls]} "
                            f"(conf={conf:.2f}, bbox={bbox})"
                        )
                    else:
                        logger.debug(f"⏭️  Skipping non-vehicle class: {cls}")
                
                logger.info(f"🚗 Filtered to {vehicle_count} vehicles from {len(boxes)} objects")
            
            return detections
            
        except Exception as e:
            logger.error(f"Vehicle detection failed: {str(e)}")
            return []
    
    async def detect_license_plate(
        self,
        frame: np.ndarray,
        bbox: Dict[str, int]
    ) -> Optional[Tuple[str, float]]:
        """
        Detect and read license plate from vehicle crop
        
        Args:
            frame: Full frame
            bbox: Bounding box of vehicle {x, y, width, height}
            
        Returns:
            Tuple of (plate_text, confidence) or None
        """
        if not self._initialized:
            await self.initialize()
        
        # Check if OCR is available
        if self.ocr_reader is None:
            logger.debug("OCR reader not available, skipping plate detection")
            return None
        
        try:
            # Extract vehicle region
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            
            # ✅ Filtrar vehículos muy pequeños (no vale la pena hacer OCR)
            if w < 60 or h < 40:
                logger.debug(f"⏭️ Vehicle too small for OCR: {w}x{h} (min: 60x40)")
                return None
            
            # ✅ Aumentar padding para capturar más área (especialmente donde está la placa)
            padding = 20  # Aumentado de 10 a 20
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(frame.shape[1], x + w + padding)
            y2 = min(frame.shape[0], y + h + padding)
            
            vehicle_crop = frame[y1:y2, x1:x2]
            
            logger.debug(f"🖼️ Vehicle crop size: {vehicle_crop.shape[1]}x{vehicle_crop.shape[0]} (bbox: {w}x{h})")
            
            if vehicle_crop.size == 0:
                logger.warning("⚠️ Empty vehicle crop, skipping OCR")
                return None
            
            # ✅ Mejorar calidad de imagen para OCR
            # Resize si es muy pequeño (mínimo 150px de ancho)
            if vehicle_crop.shape[1] < 150:
                scale = 150 / vehicle_crop.shape[1]
                new_width = 150
                new_height = int(vehicle_crop.shape[0] * scale)
                vehicle_crop = cv2.resize(vehicle_crop, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                logger.debug(f"   🔍 Resized to: {new_width}x{new_height}")
            
            # ✅ Estrategia: Probar MÚLTIPLES versiones de la imagen y tomar la mejor
            # Versión 1: Original (a veces funciona mejor)
            # Versión 2: Escala de grises con CLAHE (mejor contraste)
            # Versión 3: Con sharpening (mejora bordes de texto)
            images_to_try = [vehicle_crop]  # Original primero
            
            # Crear versión mejorada con CLAHE (sin threshold binario que puede ser demasiado agresivo)
            if len(vehicle_crop.shape) == 3:
                gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
            else:
                gray = vehicle_crop
            
            # CLAHE para mejorar contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            images_to_try.append(enhanced_bgr)
            
            # Versión 3: Aplicar sharpening para mejorar bordes de texto
            kernel_sharpening = np.array([
                [-1, -1, -1],
                [-1,  9, -1],
                [-1, -1, -1]
            ])
            sharpened = cv2.filter2D(vehicle_crop, -1, kernel_sharpening)
            images_to_try.append(sharpened)
            
            logger.debug(f"   🎨 Will try {len(images_to_try)} image versions for OCR")
            
            # Run OCR in thread pool for each version
            all_results = []
            for idx, img in enumerate(images_to_try):
                results = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    lambda i=img: self.ocr_reader.readtext(
                        i,
                        detail=1,              # Return bbox, text, confidence
                        paragraph=False,       # Detect by line/word, not paragraph
                        min_size=10,          # ✅ Detect smaller text (default: 20)
                        text_threshold=0.3,   # ✅ Lower text detection threshold
                        low_text=0.2,         # ✅ More permissive for weak text
                        link_threshold=0.2,   # ✅ Link text boxes more easily
                        canvas_size=2560,     # ✅ Internal resolution (default: 2560)
                        mag_ratio=1.5,        # ✅ Magnification ratio for better detection
                        slope_ths=0.3,        # ✅ Allow more text rotation
                        ycenter_ths=0.5,      # ✅ Y-center threshold for grouping
                        height_ths=0.7,       # ✅ Height ratio for grouping
                        width_ths=0.9,        # ✅ Width threshold
                        add_margin=0.15       # ✅ Add margin around detected text
                    )
                )
                if results:
                    logger.debug(f"   📊 Version {idx+1}: {len(results)} text(s) detected")
                    all_results.extend(results)
            
            # Usar todos los resultados combinados
            results = all_results
            
            logger.info(f"🔍 OCR raw results: {len(results)} text(s) detected")
            
            # Process OCR results
            plates = []
            for (bbox, text, conf) in results:
                logger.debug(f"   📝 Raw text: '{text}' (conf: {conf:.2f})")
                
                # Clean text: remove spaces, keep only alphanumeric and hyphens
                text = text.replace(' ', '').upper()
                text = ''.join(c for c in text if c.isalnum() or c == '-')
                
                logger.debug(f"   📝 Cleaned text: '{text}'")
                
                # ✅ Filtrar por confianza mínima (REDUCIDO a 0.2 con parámetros avanzados de EasyOCR)
                if conf < 0.2:
                    logger.debug(f"   ⚠️ Low confidence: {conf:.2f} < 0.2")
                    continue
                
                # Validate plate format (basic)
                if self._is_valid_plate_format(text):
                    # ✅ Normalizar placa al formato con guion
                    normalized_text = self._normalize_plate(text)
                    logger.info(f"   ✅ Valid plate format: '{text}' → '{normalized_text}' (conf: {conf:.2f})")
                    plates.append((normalized_text, conf))
                else:
                    logger.debug(f"   ❌ Invalid plate format: '{text}'")
            
            # Return best match
            if plates:
                plates.sort(key=lambda x: x[1], reverse=True)
                logger.info(f"🎯 Best plate match: '{plates[0][0]}' (conf: {plates[0][1]:.2f})")
                return plates[0]
            
            logger.warning(f"⚠️ No valid plates found from {len(results)} OCR results")
            return None
            
        except Exception as e:
            logger.error(f"License plate detection failed: {str(e)}")
            return None
    
    def _is_valid_plate_format(self, text: str) -> bool:
        """
        Validate license plate format (Peru format)
        Formatos válidos:
        - ABC123 (6 chars) → ABC-123
        - ABC1234 (7 chars) → ABC-1234  
        - B7J482 (6 chars) → B7J-482
        - AB1234 (6 chars) → AB-1234
        
        ✅ VALIDACIÓN FLEXIBLE: Acepta 6-7 caracteres alfanuméricos
        """
        # Longitud debe ser 6 o 7 caracteres (sin guion)
        if len(text) < 6 or len(text) > 7:
            return False
        
        # Debe contener al menos una letra Y un número
        has_letter = any(c.isalpha() for c in text)
        has_number = any(c.isdigit() for c in text)
        
        if not (has_letter and has_number):
            return False
        
        # ✅ Validar patrones comunes de placas peruanas:
        # Patrón 1: 3 letras + 3-4 números (ABC123, ABC1234)
        if len(text) >= 6:
            letters_start = text[:3]
            numbers_end = text[3:]
            if letters_start.isalpha() and numbers_end.isdigit():
                return True
        
        # Patrón 2: 2 letras + 4 números (AB1234)
        if len(text) == 6:
            letters_start = text[:2]
            numbers_end = text[2:]
            if letters_start.isalpha() and numbers_end.isdigit():
                return True
        
        # Patrón 3: Letra+Número+Letra+3 números (B7J482, A1B234)
        if len(text) == 6:
            if text[0].isalpha() and text[1].isdigit() and text[2].isalpha() and text[3:].isdigit():
                return True
        
        return False
    
    def _normalize_plate(self, text: str) -> str:
        """
        Normalizar placa al formato con guion
        ABC123 → ABC-123
        ABC1234 → ABC-1234
        B7J482 → B7J-482
        AB1234 → AB-1234
        """
        # Si ya tiene guion, retornar tal cual
        if '-' in text:
            return text
        
        # Patrón 1: 3 letras + 3-4 números (ABC123 → ABC-123, ABC1234 → ABC-1234)
        if len(text) >= 6 and text[:3].isalpha() and text[3:].isdigit():
            return f"{text[:3]}-{text[3:]}"
        
        # Patrón 2: 2 letras + 4 números (AB1234 → AB-1234)
        if len(text) == 6 and text[:2].isalpha() and text[2:].isdigit():
            return f"{text[:2]}-{text[2:]}"
        
        # Patrón 3: Letra+Número+Letra+3 números (B7J482 → B7J-482)
        if len(text) == 6 and text[0].isalpha() and text[1].isdigit() and text[2].isalpha() and text[3:].isdigit():
            return f"{text[:3]}-{text[3:]}"
        
        # Si no coincide con ningún patrón, retornar tal cual
        return text
    
    async def estimate_speed(
        self,
        detections_history: List[Dict],
        fps: float,
        calibration_data: Optional[Dict] = None
    ) -> Optional[float]:
        """
        Estimate vehicle speed based on tracking history
        
        Args:
            detections_history: List of detections over time
            fps: Frames per second
            calibration_data: Camera calibration data
            
        Returns:
            Estimated speed in km/h or None
        """
        # Simplified speed estimation for MVP
        # In production, use proper optical flow and Kalman filtering
        
        if len(detections_history) < 2:
            return None
        
        try:
            # Calculate pixel displacement
            first = detections_history[0]
            last = detections_history[-1]
            
            x1 = first['bbox']['x'] + first['bbox']['width'] / 2
            y1 = first['bbox']['y'] + first['bbox']['height'] / 2
            
            x2 = last['bbox']['x'] + last['bbox']['width'] / 2
            y2 = last['bbox']['y'] + last['bbox']['height'] / 2
            
            pixel_distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            # Time elapsed
            time_elapsed = len(detections_history) / fps
            
            # Simplified conversion: assume 1 pixel ≈ 0.05 meters (needs calibration)
            # This is a placeholder - real implementation needs camera calibration
            meters_per_pixel = 0.05
            if calibration_data and 'meters_per_pixel' in calibration_data:
                meters_per_pixel = calibration_data['meters_per_pixel']
            
            distance_meters = pixel_distance * meters_per_pixel
            speed_ms = distance_meters / time_elapsed
            speed_kmh = speed_ms * 3.6
            
            # Sanity check
            if speed_kmh > 0 and speed_kmh < 200:
                return round(speed_kmh, 1)
            
            return None
            
        except Exception as e:
            logger.error(f"Speed estimation failed: {str(e)}")
            return None
    
    async def detect_traffic_light(
        self,
        frame: np.ndarray,
        roi: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Detect traffic light state in frame
        
        Args:
            frame: Input frame
            roi: Region of interest (x1, y1, x2, y2) or None for auto-detect
            
        Returns:
            Dict with 'state', 'confidence', 'bbox' or None
        """
        if not self._initialized:
            await self.initialize()
        
        if self.traffic_light_detector is None:
            logger.debug("Traffic light detector not available")
            return None
        
        try:
            detection = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.traffic_light_detector.detect(frame, roi)
            )
            
            logger.debug(
                f"🚦 Traffic light: {detection['state']} "
                f"(confidence={detection['confidence']:.2f})"
            )
            
            return detection
            
        except Exception as e:
            logger.error(f"Traffic light detection failed: {str(e)}")
            return None
    
    def is_red_light(self, traffic_light_detection: Optional[Dict[str, Any]]) -> bool:
        """
        Check if traffic light is red
        
        Args:
            traffic_light_detection: Detection result from detect_traffic_light
            
        Returns:
            True if light is red with sufficient confidence
        """
        if traffic_light_detection is None:
            return False
        
        if self.traffic_light_detector is None:
            return False
        
        return self.traffic_light_detector.is_red(traffic_light_detection)
    
    async def detect_lanes(
        self,
        frame: np.ndarray,
        roi_vertices: Optional[np.ndarray] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Detect lane markings in frame
        
        Args:
            frame: Input frame
            roi_vertices: ROI vertices for lane detection
            
        Returns:
            Dict with 'lanes', 'has_center_line', 'lane_count' or None
        """
        if not self._initialized:
            await self.initialize()
        
        if self.lane_detector is None:
            logger.debug("Lane detector not available")
            return None
        
        try:
            detection = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.lane_detector.detect(frame, roi_vertices)
            )
            
            logger.debug(
                f"🛣️ Lanes detected: {detection['lane_count']} lanes "
                f"(center: {detection['has_center_line']})"
            )
            
            return detection
            
        except Exception as e:
            logger.error(f"Lane detection failed: {str(e)}")
            return None
    
    def check_lane_violation(
        self,
        vehicle_bbox: Tuple[float, float, float, float],
        lane_detection: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if vehicle is violating lane rules
        
        Args:
            vehicle_bbox: Vehicle bounding box [x1, y1, x2, y2]
            lane_detection: Lane detection result
            
        Returns:
            Dict with violation info or None
        """
        if self.lane_detector is None:
            return None
        
        if lane_detection is None:
            return None
        
        lanes = lane_detection.get('lanes', {})
        if not lanes:
            return None
        
        return self.lane_detector.check_violation(vehicle_bbox, lanes)
    
    def shutdown(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
        logger.info("Model service shut down")


# Global model service instance
model_service = ModelService()
