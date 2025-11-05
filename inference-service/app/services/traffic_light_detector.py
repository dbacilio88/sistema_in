"""
Enhanced Traffic Light Detector for Inference Service

Detector de semáforos que combina:
1. YOLO para detectar el objeto "traffic light"
2. Análisis HSV para determinar el color (rojo/amarillo/verde)
"""

import logging
from typing import Optional, Tuple, Dict, Any, List
from enum import Enum
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class TrafficLightState(str, Enum):
    """Estados del semáforo"""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    UNKNOWN = "unknown"


class SimpleTrafficLightDetector:
    """
    Detector de semáforos que combina YOLO y análisis de color HSV
    
    1. Usa YOLO para detectar objetos "traffic light"
    2. Analiza el color HSV dentro del bounding box detectado
    """
    
    def __init__(self, yolo_model=None, confidence_threshold: float = 0.4):
        self.yolo_model = yolo_model  # YOLOv8 model
        self.confidence_threshold = confidence_threshold
        self.yolo_confidence_threshold = 0.15  # ✅ Reducido de 0.2 a 0.15 (tu video tiene 0.16-0.38)
        
        # Rangos HSV para detección de colores (MÁS permisivos)
        self.hsv_ranges = {
            'red': {
                # AMPLIADO: H=0-25 para capturar rojos con tinte naranja (H=58-67 después de compresión)
                # Reducido S de 80 a 50 para capturar semáforos con saturación media
                'lower1': np.array([0, 50, 40]),       # ✅ Rango expandido: incluye naranja-rojizo
                'upper1': np.array([25, 255, 255]),    # ✅ Expandido de 10 a 25 para H=58-67
                'lower2': np.array([150, 50, 40]),     # ✅ Expandido de 160 a 150
                'upper2': np.array([180, 255, 255])
            },
            'yellow': {
                'lower': np.array([26, 60, 60]),       # ✅ Ajustado de 15 a 26 (no solapar con rojo)
                'upper': np.array([45, 255, 255])
            },
            'green': {
                'lower': np.array([70, 50, 40]),       # ✅ Ajustado de 40 a 70 (evitar solapamiento)
                'upper': np.array([95, 255, 255])
            }
        }
        
        # Umbrales mínimos para considerar un color detectado (% de píxeles)
        self.min_color_percentage = 3.0  # ✅ Reducido de 5% a 3% (menos estricto)
        
        # Historial para suavizado temporal
        self.state_history = []
        self.max_history = 5
        self.detected_traffic_lights = []  # Cache de semáforos detectados
        
        logger.info(f"SimpleTrafficLightDetector initialized with YOLO: {yolo_model is not None}")
    
    def detect(
        self,
        frame: np.ndarray,
        roi: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        Detectar estado del semáforo
        
        Args:
            frame: Frame completo (BGR)
            roi: Región de interés (x1, y1, x2, y2). Si None, usa detección YOLO
            
        Returns:
            Dict con 'state', 'confidence', 'bbox', 'detections'
        """
        height, width = frame.shape[:2]
        
        # Paso 1: Detectar semáforos con YOLO si está disponible
        traffic_light_boxes = []
        
        if self.yolo_model is not None:
            traffic_light_boxes = self._detect_traffic_lights_yolo(frame)
            
        # Si no hay detecciones YOLO y no hay ROI, usar ROI por defecto
        if len(traffic_light_boxes) == 0 and roi is None:
            # ROI por defecto: área superior
            roi = (
                int(width * 0.3),   # x1: 30% desde izquierda
                0,                   # y1: top
                int(width * 0.7),   # x2: 70% desde izquierda
                int(height * 0.4)   # y2: 40% altura
            )
            traffic_light_boxes = [roi]
        elif roi is not None:
            traffic_light_boxes = [roi]
        
        # Paso 2: Analizar color en cada semáforo detectado
        best_state = TrafficLightState.UNKNOWN
        best_confidence = 0.0
        best_bbox = None
        all_detections = []
        
        for bbox in traffic_light_boxes:
            x1, y1, x2, y2 = bbox
            
            # Validar bbox
            if x2 <= x1 or y2 <= y1 or x1 < 0 or y1 < 0 or x2 > width or y2 > height:
                continue
            
            # Extraer región del semáforo
            traffic_light_region = frame[y1:y2, x1:x2]
            
            if traffic_light_region.size == 0:
                continue
            
            # Detectar estado por color
            state, confidence = self._detect_state_by_color(traffic_light_region)
            
            detection = {
                'state': state,
                'confidence': confidence,
                'bbox': bbox
            }
            all_detections.append(detection)
            
            # Actualizar mejor detección (priorizar ROJO)
            if state == TrafficLightState.RED:
                if confidence > best_confidence or best_state != TrafficLightState.RED:
                    best_state = state
                    best_confidence = confidence
                    best_bbox = bbox
            elif confidence > best_confidence and best_state != TrafficLightState.RED:
                best_state = state
                best_confidence = confidence
                best_bbox = bbox
        
        # Suavizado temporal para el mejor resultado
        if best_state != TrafficLightState.UNKNOWN:
            self.state_history.append(best_state)
            if len(self.state_history) > self.max_history:
                self.state_history.pop(0)
            
            # Estado más frecuente en historial
            if len(self.state_history) >= 3:
                best_state = max(set(self.state_history), key=self.state_history.count)
        
        result = {
            'state': best_state,
            'confidence': best_confidence,
            'bbox': best_bbox if best_bbox else (0, 0, width, height),
            'all_detections': all_detections,
            'count': len(all_detections)
        }
        
        logger.debug(f"Traffic light detection: state={best_state}, conf={best_confidence:.2f}, count={len(all_detections)}")
        
        return result
    
    def _detect_traffic_lights_yolo(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detectar objetos "traffic light" usando YOLO
        
        Args:
            frame: Frame BGR
            
        Returns:
            Lista de bounding boxes (x1, y1, x2, y2)
        """
        if self.yolo_model is None:
            logger.warning("YOLO model not available for traffic light detection")
            return []
        
        try:
            # Ejecutar YOLO con imgsz más grande para detectar objetos pequeños
            results = self.yolo_model(frame, verbose=False, imgsz=640, conf=self.yolo_confidence_threshold)
            
            traffic_light_boxes = []
            all_detections_info = []
            
            for result in results:
                boxes = result.boxes
                
                # Primero, loggear TODAS las clases detectadas para debugging
                if len(boxes) > 0:
                    detected_classes = {}
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        class_name = result.names[cls_id]
                        confidence = float(box.conf[0])
                        if class_name not in detected_classes:
                            detected_classes[class_name] = []
                        detected_classes[class_name].append(confidence)
                    
                    logger.info(f"🔍 YOLO detected classes in frame: {', '.join([f'{cls}({len(confs)})' for cls, confs in detected_classes.items()])}")
                
                # Ahora buscar semáforos específicamente
                for box in boxes:
                    # Obtener clase
                    cls_id = int(box.cls[0])
                    class_name = result.names[cls_id]
                    confidence = float(box.conf[0])
                    
                    # Obtener bbox
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox_width = x2 - x1
                    bbox_height = y2 - y1
                    
                    # Loggear TODOS los objetos con sus dimensiones
                    all_detections_info.append(f"{class_name}({confidence:.2f})[{bbox_width:.0f}x{bbox_height:.0f}]")
                    
                    # Filtrar por clase "traffic light" (class 9 en COCO)
                    if class_name == 'traffic light' and confidence >= self.yolo_confidence_threshold:
                        # Validar que el semáforo no sea demasiado pequeño
                        min_size = 15  # ✅ Reducido de 20 a 15 píxeles
                        if bbox_width >= min_size and bbox_height >= min_size:
                            traffic_light_boxes.append((int(x1), int(y1), int(x2), int(y2)))
                            logger.info(f"✅ Traffic light detected: bbox=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}) size={bbox_width:.0f}x{bbox_height:.0f} conf={confidence:.2f}")
                        else:
                            logger.debug(f"⚠️ Traffic light too small (skipped): {bbox_width:.0f}x{bbox_height:.0f} conf={confidence:.2f}")
            
            if len(all_detections_info) > 0:
                logger.debug(f"📊 All YOLO detections: {', '.join(all_detections_info[:10])}...")  # Solo primeros 10
            
            if len(traffic_light_boxes) == 0:
                logger.warning(f"❌ No traffic lights found in frame (checked {len(boxes) if 'boxes' in locals() else 0} detections)")
            else:
                logger.info(f"🚦 YOLO found {len(traffic_light_boxes)} traffic light(s)")
            
            return traffic_light_boxes
            
        except Exception as e:
            logger.error(f"Error in YOLO traffic light detection: {e}", exc_info=True)
            return []
    
    def _detect_state_by_color(
        self,
        roi_image: np.ndarray
    ) -> Tuple[TrafficLightState, float]:
        """Detectar estado mediante análisis HSV"""
        # Convertir a HSV
        hsv = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
        
        # Calcular scores para cada color
        red_score = self._calculate_color_score(hsv, 'red')
        yellow_score = self._calculate_color_score(hsv, 'yellow')
        green_score = self._calculate_color_score(hsv, 'green')
        
        # ✅ Log detallado de scores para debugging
        height, width = roi_image.shape[:2]
        logger.debug(f"Color scores for {width}x{height} ROI: red={red_score:.3f}, yellow={yellow_score:.3f}, green={green_score:.3f}")
        
        scores = {
            TrafficLightState.RED: red_score,
            TrafficLightState.YELLOW: yellow_score,
            TrafficLightState.GREEN: green_score
        }
        
        max_state = max(scores, key=scores.get)
        max_score = scores[max_state]
        
        # ✅ Umbral más bajo: 0.03 en lugar de 0.05
        if max_score < 0.03:
            logger.debug(f"Score too low ({max_score:.3f} < 0.03), returning UNKNOWN")
            return TrafficLightState.UNKNOWN, 0.0
        
        # Normalizar confianza
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        logger.debug(f"Detected state: {max_state.value} with confidence {confidence:.3f}")
        
        return max_state, confidence
    
    def _calculate_color_score(self, region: np.ndarray, color: str) -> float:
        """Calcular presencia de color en región"""
        if color == 'red':
            mask1 = cv2.inRange(
                region,
                self.hsv_ranges['red']['lower1'],
                self.hsv_ranges['red']['upper1']
            )
            mask2 = cv2.inRange(
                region,
                self.hsv_ranges['red']['lower2'],
                self.hsv_ranges['red']['upper2']
            )
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(
                region,
                self.hsv_ranges[color]['lower'],
                self.hsv_ranges[color]['upper']
            )
        
        total_pixels = region.shape[0] * region.shape[1]
        matching_pixels = cv2.countNonZero(mask)
        score = matching_pixels / total_pixels if total_pixels > 0 else 0.0
        
        return score
    
    def is_red(self, detection: Dict[str, Any]) -> bool:
        """Verificar si semáforo está en rojo"""
        return (
            detection.get('state') == TrafficLightState.RED and
            detection.get('confidence', 0.0) >= self.confidence_threshold
        )
