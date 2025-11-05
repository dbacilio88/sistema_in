"""
Traffic Light Detection and State Classification

Detecta semáforos y clasifica su estado (rojo, amarillo, verde)
usando YOLOv8 para detección y clasificación de color
"""

import time
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import numpy as np
import cv2
import onnxruntime as ort

from src.config import ml_settings

logger = logging.getLogger(__name__)


class TrafficLightState(str, Enum):
    """Estados del semáforo"""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    UNKNOWN = "unknown"
    OFF = "off"


@dataclass
class TrafficLightDetection:
    """Resultado de detección de semáforo"""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    state: TrafficLightState
    confidence: float
    position: str  # 'top', 'middle', 'bottom' para múltiples luces
    timestamp: float


class TrafficLightDetector:
    """
    Detector de semáforos usando análisis de color HSV
    
    Estrategia:
    1. Detectar región de semáforo (puede usar YOLO o región fija configurada)
    2. Analizar color dominante en cada luz (superior, media, inferior)
    3. Clasificar estado basado en intensidad de color rojo/amarillo/verde
    """
    
    def __init__(
        self,
        use_yolo: bool = False,
        model_path: Optional[Path] = None,
        confidence_threshold: float = 0.6
    ):
        """
        Inicializar detector de semáforos
        
        Args:
            use_yolo: Si usar modelo YOLO para detectar semáforo (False = región fija)
            model_path: Ruta al modelo YOLO para semáforos (opcional)
            confidence_threshold: Umbral mínimo de confianza
        """
        self.use_yolo = use_yolo
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.session = None
        
        # Configuración de detección de color HSV
        self.hsv_ranges = {
            'red': {
                'lower1': np.array([0, 100, 100]),    # Rojo inferior
                'upper1': np.array([10, 255, 255]),
                'lower2': np.array([160, 100, 100]),  # Rojo superior
                'upper2': np.array([180, 255, 255])
            },
            'yellow': {
                'lower': np.array([15, 100, 100]),
                'upper': np.array([35, 255, 255])
            },
            'green': {
                'lower': np.array([40, 50, 50]),
                'upper': np.array([90, 255, 255])
            }
        }
        
        # Región de interés del semáforo (se puede configurar por zona)
        self.traffic_light_roi: Optional[Tuple[int, int, int, int]] = None
        
        # Historial de estados para suavizado temporal
        self.state_history: List[TrafficLightState] = []
        self.max_history = 5
        
        logger.info(f"TrafficLightDetector initialized (YOLO: {use_yolo})")
        
        if use_yolo and model_path:
            self._load_yolo_model()
    
    def _load_yolo_model(self):
        """Cargar modelo YOLO para detección de semáforos"""
        try:
            providers = ml_settings.get_onnx_providers()
            self.session = ort.InferenceSession(
                str(self.model_path),
                providers=providers
            )
            logger.info(f"Traffic light YOLO model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load traffic light model: {e}")
            self.use_yolo = False
    
    def set_roi(self, roi: Tuple[int, int, int, int]):
        """
        Configurar región de interés del semáforo
        
        Args:
            roi: (x1, y1, x2, y2) coordenadas de la región del semáforo
        """
        self.traffic_light_roi = roi
        logger.info(f"Traffic light ROI set to: {roi}")
    
    def detect(
        self, 
        frame: np.ndarray,
        roi: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[TrafficLightDetection]:
        """
        Detectar estado del semáforo en el frame
        
        Args:
            frame: Frame de video (BGR)
            roi: Región de interés opcional (x1, y1, x2, y2)
            
        Returns:
            TrafficLightDetection o None si no se detecta
        """
        start_time = time.time()
        
        # Usar ROI provista o la configurada
        roi = roi or self.traffic_light_roi
        
        if roi is None:
            logger.warning("No ROI set for traffic light detection")
            return None
        
        # Extraer región del semáforo
        x1, y1, x2, y2 = roi
        traffic_light_region = frame[y1:y2, x1:x2]
        
        if traffic_light_region.size == 0:
            return None
        
        # Detectar estado por análisis de color
        state, confidence = self._detect_state_by_color(traffic_light_region)
        
        # Suavizado temporal
        self.state_history.append(state)
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
        
        # Estado más común en el historial
        if len(self.state_history) >= 3:
            state = max(set(self.state_history), key=self.state_history.count)
        
        detection_time = (time.time() - start_time) * 1000
        
        detection = TrafficLightDetection(
            bbox=roi,
            state=state,
            confidence=confidence,
            position='center',
            timestamp=time.time()
        )
        
        logger.debug(
            f"Traffic light detected: {state.value} "
            f"(conf={confidence:.2f}, time={detection_time:.1f}ms)"
        )
        
        return detection
    
    def _detect_state_by_color(
        self, 
        roi_image: np.ndarray
    ) -> Tuple[TrafficLightState, float]:
        """
        Detectar estado del semáforo mediante análisis de color HSV
        
        Args:
            roi_image: Imagen de la región del semáforo
            
        Returns:
            Tupla (estado, confianza)
        """
        # Convertir a HSV
        hsv = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
        
        # Dividir en 3 regiones (superior, media, inferior)
        height = hsv.shape[0]
        top_region = hsv[0:height//3, :]
        middle_region = hsv[height//3:2*height//3, :]
        bottom_region = hsv[2*height//3:, :]
        
        # Analizar cada región
        red_score_top = self._calculate_color_score(top_region, 'red')
        yellow_score_middle = self._calculate_color_score(middle_region, 'yellow')
        green_score_bottom = self._calculate_color_score(bottom_region, 'green')
        
        # También verificar todas las regiones para cada color
        red_score_all = self._calculate_color_score(hsv, 'red')
        yellow_score_all = self._calculate_color_score(hsv, 'yellow')
        green_score_all = self._calculate_color_score(hsv, 'green')
        
        # Determinar estado
        scores = {
            TrafficLightState.RED: max(red_score_top, red_score_all),
            TrafficLightState.YELLOW: max(yellow_score_middle, yellow_score_all),
            TrafficLightState.GREEN: max(green_score_bottom, green_score_all)
        }
        
        max_state = max(scores, key=scores.get)
        max_score = scores[max_state]
        
        # Si el score es muy bajo, considerar desconocido
        if max_score < 0.1:
            return TrafficLightState.UNKNOWN, 0.0
        
        # Normalizar confianza
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        return max_state, confidence
    
    def _calculate_color_score(self, region: np.ndarray, color: str) -> float:
        """
        Calcular score de presencia de un color en la región
        
        Args:
            region: Región HSV
            color: 'red', 'yellow', o 'green'
            
        Returns:
            Score de 0 a 1
        """
        if color == 'red':
            # Rojo requiere dos rangos (wraparound de Hue)
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
        
        # Calcular porcentaje de píxeles que coinciden
        total_pixels = region.shape[0] * region.shape[1]
        matching_pixels = cv2.countNonZero(mask)
        score = matching_pixels / total_pixels if total_pixels > 0 else 0.0
        
        return score
    
    def visualize_detection(
        self,
        frame: np.ndarray,
        detection: Optional[TrafficLightDetection]
    ) -> np.ndarray:
        """
        Dibujar detección en el frame
        
        Args:
            frame: Frame original
            detection: Detección de semáforo
            
        Returns:
            Frame anotado
        """
        annotated = frame.copy()
        
        if detection is None:
            return annotated
        
        x1, y1, x2, y2 = detection.bbox
        
        # Color del borde según estado
        color_map = {
            TrafficLightState.RED: (0, 0, 255),
            TrafficLightState.YELLOW: (0, 255, 255),
            TrafficLightState.GREEN: (0, 255, 0),
            TrafficLightState.UNKNOWN: (128, 128, 128),
            TrafficLightState.OFF: (64, 64, 64)
        }
        
        color = color_map.get(detection.state, (255, 255, 255))
        
        # Dibujar bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
        
        # Etiqueta
        label = f"Traffic Light: {detection.state.value.upper()}"
        confidence_label = f"{detection.confidence * 100:.0f}%"
        
        # Fondo del texto
        (w1, h1), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        (w2, h2), _ = cv2.getTextSize(confidence_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        
        cv2.rectangle(annotated, (x1, y1 - h1 - h2 - 10), (x1 + max(w1, w2) + 10, y1), color, -1)
        
        # Texto
        cv2.putText(annotated, label, (x1 + 5, y1 - h2 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated, confidence_label, (x1 + 5, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated
    
    def is_red(self, detection: Optional[TrafficLightDetection]) -> bool:
        """
        Verificar si el semáforo está en rojo
        
        Args:
            detection: Detección de semáforo
            
        Returns:
            True si está en rojo con suficiente confianza
        """
        if detection is None:
            return False
        
        return (
            detection.state == TrafficLightState.RED and
            detection.confidence >= self.confidence_threshold
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del detector"""
        if not self.state_history:
            return {}
        
        from collections import Counter
        state_counts = Counter(self.state_history)
        
        return {
            'history_length': len(self.state_history),
            'state_distribution': dict(state_counts),
            'current_state': self.state_history[-1].value if self.state_history else None,
            'use_yolo': self.use_yolo
        }


def create_traffic_light_detector(
    use_yolo: bool = False,
    model_path: Optional[Path] = None
) -> TrafficLightDetector:
    """Factory function para crear detector de semáforos"""
    return TrafficLightDetector(use_yolo=use_yolo, model_path=model_path)
