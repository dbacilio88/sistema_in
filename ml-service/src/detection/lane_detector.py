"""
Lane Detection and Invasion Detection

Detecta carriles en la carretera y determina si vehículos invaden carriles incorrectos
usando detección de líneas Hough y análisis de posición
"""

import time
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class LaneViolationType(str, Enum):
    """Tipos de violación de carril"""
    CROSSED_SOLID = "crossed_solid_line"
    WRONG_SIDE = "wrong_side_driving"
    IMPROPER_LANE_CHANGE = "improper_lane_change"
    CENTER_LINE_VIOLATION = "center_line_violation"


@dataclass
class Lane:
    """Representación de un carril detectado"""
    points: List[Tuple[int, int]]  # Puntos de la línea del carril
    slope: float
    intercept: float
    side: str  # 'left', 'right', 'center'
    is_solid: bool  # True si es línea sólida
    confidence: float


@dataclass
class LaneViolation:
    """Violación de carril detectada"""
    violation_type: LaneViolationType
    vehicle_bbox: Tuple[int, int, int, int]
    lane_crossed: Lane
    position: Tuple[int, int]  # Centro del vehículo
    confidence: float
    timestamp: float


class LaneDetector:
    """
    Detector de carriles usando Hough Lines y análisis de región
    
    Estrategia:
    1. Preprocesar imagen (grayscale, blur, edge detection)
    2. Aplicar máscara de región de interés (ROI)
    3. Detectar líneas usando Hough Transform
    4. Clasificar líneas en carriles (izquierda, derecha, centro)
    5. Determinar si vehículos cruzan líneas prohibidas
    """
    
    def __init__(
        self,
        roi_vertices: Optional[np.ndarray] = None,
        confidence_threshold: float = 0.6
    ):
        """
        Inicializar detector de carriles
        
        Args:
            roi_vertices: Vértices del polígono ROI [(x1,y1), (x2,y2), ...]
            confidence_threshold: Umbral mínimo de confianza
        """
        self.roi_vertices = roi_vertices
        self.confidence_threshold = confidence_threshold
        
        # Parámetros de Canny Edge Detection
        self.canny_low = 50
        self.canny_high = 150
        
        # Parámetros de Hough Transform
        self.hough_rho = 2
        self.hough_theta = np.pi / 180
        self.hough_threshold = 50
        self.hough_min_line_length = 100
        self.hough_max_line_gap = 50
        
        # Carriles detectados
        self.lanes: Dict[str, Lane] = {}
        
        # Historial de detecciones para estabilidad
        self.lane_history: List[Dict[str, Lane]] = []
        self.max_history = 5
        
        logger.info("LaneDetector initialized")
    
    def set_roi(self, vertices: np.ndarray):
        """
        Configurar región de interés
        
        Args:
            vertices: Array de vértices [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
        """
        self.roi_vertices = vertices
        logger.info(f"ROI set with {len(vertices)} vertices")
    
    def detect_lanes(self, frame: np.ndarray) -> Dict[str, Lane]:
        """
        Detectar carriles en el frame
        
        Args:
            frame: Frame de video (BGR)
            
        Returns:
            Diccionario de carriles detectados {'left': Lane, 'right': Lane, ...}
        """
        start_time = time.time()
        
        # Preprocesar
        edges = self._preprocess(frame)
        
        # Aplicar máscara ROI
        if self.roi_vertices is not None:
            masked_edges = self._apply_roi_mask(edges)
        else:
            # ROI por defecto (mitad inferior del frame, trapecio)
            height, width = frame.shape[:2]
            default_roi = np.array([[
                (int(width * 0.1), height),
                (int(width * 0.4), int(height * 0.6)),
                (int(width * 0.6), int(height * 0.6)),
                (int(width * 0.9), height)
            ]], dtype=np.int32)
            self.roi_vertices = default_roi[0]
            masked_edges = self._apply_roi_mask(edges)
        
        # Detectar líneas con Hough Transform
        lines = cv2.HoughLinesP(
            masked_edges,
            self.hough_rho,
            self.hough_theta,
            self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )
        
        # Clasificar y agrupar líneas en carriles
        lanes = self._classify_lanes(lines, frame.shape)
        
        # Suavizado temporal
        self.lane_history.append(lanes)
        if len(self.lane_history) > self.max_history:
            self.lane_history.pop(0)
        
        # Promediar detecciones
        if len(self.lane_history) >= 3:
            lanes = self._smooth_lanes()
        
        self.lanes = lanes
        
        detection_time = (time.time() - start_time) * 1000
        logger.debug(f"Lanes detected in {detection_time:.1f}ms: {list(lanes.keys())}")
        
        return lanes
    
    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Preprocesar frame para detección de bordes"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro Gaussiano para reducir ruido
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detectar bordes con Canny
        edges = cv2.Canny(blur, self.canny_low, self.canny_high)
        
        return edges
    
    def _apply_roi_mask(self, edges: np.ndarray) -> np.ndarray:
        """Aplicar máscara de región de interés"""
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, [self.roi_vertices], 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        return masked_edges
    
    def _classify_lanes(
        self,
        lines: Optional[np.ndarray],
        frame_shape: Tuple[int, int, int]
    ) -> Dict[str, Lane]:
        """Clasificar líneas detectadas en carriles"""
        if lines is None:
            return {}
        
        height, width = frame_shape[:2]
        left_lines = []
        right_lines = []
        center_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calcular pendiente e intercepto
            if x2 - x1 == 0:
                continue  # Evitar división por cero
            
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            
            # Filtrar líneas horizontales (slope cerca de 0)
            if abs(slope) < 0.5:
                continue
            
            # Clasificar por pendiente y posición
            x_center = (x1 + x2) / 2
            
            if slope < 0 and x_center < width * 0.5:
                # Línea izquierda (pendiente negativa, lado izquierdo)
                left_lines.append((slope, intercept, [(x1, y1), (x2, y2)]))
            elif slope > 0 and x_center > width * 0.5:
                # Línea derecha (pendiente positiva, lado derecho)
                right_lines.append((slope, intercept, [(x1, y1), (x2, y2)]))
            elif abs(x_center - width * 0.5) < width * 0.2:
                # Línea central
                center_lines.append((slope, intercept, [(x1, y1), (x2, y2)]))
        
        lanes = {}
        
        # Crear lane para el lado izquierdo
        if left_lines:
            avg_slope = np.mean([s for s, _, _ in left_lines])
            avg_intercept = np.mean([i for _, i, _ in left_lines])
            all_points = [p for _, _, points in left_lines for p in points]
            
            lanes['left'] = Lane(
                points=all_points,
                slope=avg_slope,
                intercept=avg_intercept,
                side='left',
                is_solid=True,  # Asumir sólida por defecto
                confidence=0.8
            )
        
        # Crear lane para el lado derecho
        if right_lines:
            avg_slope = np.mean([s for s, _, _ in right_lines])
            avg_intercept = np.mean([i for _, i, _ in right_lines])
            all_points = [p for _, _, points in right_lines for p in points]
            
            lanes['right'] = Lane(
                points=all_points,
                slope=avg_slope,
                intercept=avg_intercept,
                side='right',
                is_solid=True,
                confidence=0.8
            )
        
        # Crear lane para el centro
        if center_lines:
            avg_slope = np.mean([s for s, _, _ in center_lines])
            avg_intercept = np.mean([i for _, i, _ in center_lines])
            all_points = [p for _, _, points in center_lines for p in points]
            
            lanes['center'] = Lane(
                points=all_points,
                slope=avg_slope,
                intercept=avg_intercept,
                side='center',
                is_solid=True,  # Línea central suele ser sólida
                confidence=0.9
            )
        
        return lanes
    
    def _smooth_lanes(self) -> Dict[str, Lane]:
        """Suavizar detecciones de carriles usando historial"""
        smoothed = {}
        
        # Para cada tipo de carril (left, right, center)
        for side in ['left', 'right', 'center']:
            slopes = []
            intercepts = []
            
            for lanes_dict in self.lane_history:
                if side in lanes_dict:
                    slopes.append(lanes_dict[side].slope)
                    intercepts.append(lanes_dict[side].intercept)
            
            if slopes and intercepts:
                avg_slope = np.mean(slopes)
                avg_intercept = np.mean(intercepts)
                
                # Usar los puntos más recientes
                recent_lane = self.lane_history[-1].get(side)
                if recent_lane:
                    smoothed[side] = Lane(
                        points=recent_lane.points,
                        slope=avg_slope,
                        intercept=avg_intercept,
                        side=side,
                        is_solid=recent_lane.is_solid,
                        confidence=recent_lane.confidence
                    )
        
        return smoothed
    
    def check_lane_violation(
        self,
        vehicle_bbox: Tuple[int, int, int, int],
        vehicle_center: Tuple[int, int]
    ) -> Optional[LaneViolation]:
        """
        Verificar si el vehículo está invadiendo un carril
        
        Args:
            vehicle_bbox: Bounding box del vehículo (x1, y1, x2, y2)
            vehicle_center: Centro del vehículo (x, y)
            
        Returns:
            LaneViolation si hay violación, None en caso contrario
        """
        if not self.lanes:
            return None
        
        x_center, y_center = vehicle_center
        
        # Verificar cruce de línea central (más crítico)
        if 'center' in self.lanes:
            center_lane = self.lanes['center']
            
            # Calcular posición X de la línea central en Y del vehículo
            if center_lane.slope != 0:
                x_line = (y_center - center_lane.intercept) / center_lane.slope
                
                # Si el vehículo está muy cerca o cruza la línea central
                distance = abs(x_center - x_line)
                
                if distance < 30:  # Umbral de 30 píxeles
                    return LaneViolation(
                        violation_type=LaneViolationType.CENTER_LINE_VIOLATION,
                        vehicle_bbox=vehicle_bbox,
                        lane_crossed=center_lane,
                        position=vehicle_center,
                        confidence=0.9,
                        timestamp=time.time()
                    )
        
        # Verificar cruce de líneas laterales
        for side in ['left', 'right']:
            if side in self.lanes:
                lane = self.lanes[side]
                
                if lane.slope != 0:
                    x_line = (y_center - lane.intercept) / lane.slope
                    distance = abs(x_center - x_line)
                    
                    # Determinar si el vehículo está del lado incorrecto
                    if side == 'left' and x_center < x_line and distance < 40:
                        return LaneViolation(
                            violation_type=LaneViolationType.CROSSED_SOLID,
                            vehicle_bbox=vehicle_bbox,
                            lane_crossed=lane,
                            position=vehicle_center,
                            confidence=0.7,
                            timestamp=time.time()
                        )
                    elif side == 'right' and x_center > x_line and distance < 40:
                        return LaneViolation(
                            violation_type=LaneViolationType.CROSSED_SOLID,
                            vehicle_bbox=vehicle_bbox,
                            lane_crossed=lane,
                            position=vehicle_center,
                            confidence=0.7,
                            timestamp=time.time()
                        )
        
        return None
    
    def visualize_lanes(
        self,
        frame: np.ndarray,
        lanes: Optional[Dict[str, Lane]] = None
    ) -> np.ndarray:
        """
        Dibujar carriles detectados en el frame
        
        Args:
            frame: Frame original
            lanes: Carriles a dibujar (usa self.lanes si None)
            
        Returns:
            Frame anotado
        """
        annotated = frame.copy()
        lanes = lanes or self.lanes
        
        if not lanes:
            return annotated
        
        # Colores por tipo de carril
        colors = {
            'left': (0, 255, 0),     # Verde
            'right': (0, 255, 0),    # Verde
            'center': (0, 0, 255)    # Rojo (más crítico)
        }
        
        height = frame.shape[0]
        
        for side, lane in lanes.items():
            color = colors.get(side, (255, 255, 255))
            
            # Dibujar línea del carril
            if lane.slope != 0:
                y1 = height
                y2 = int(height * 0.6)
                x1 = int((y1 - lane.intercept) / lane.slope)
                x2 = int((y2 - lane.intercept) / lane.slope)
                
                # Línea más gruesa si es sólida
                thickness = 5 if lane.is_solid else 3
                cv2.line(annotated, (x1, y1), (x2, y2), color, thickness)
                
                # Etiqueta
                label = f"{side.upper()} ({'SOLID' if lane.is_solid else 'DASHED'})"
                cv2.putText(
                    annotated,
                    label,
                    (x2 + 10, y2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )
        
        # Dibujar ROI
        if self.roi_vertices is not None:
            cv2.polylines(
                annotated,
                [self.roi_vertices],
                isClosed=True,
                color=(255, 0, 255),
                thickness=2
            )
        
        return annotated
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del detector"""
        return {
            'lanes_detected': len(self.lanes),
            'lane_types': list(self.lanes.keys()),
            'history_length': len(self.lane_history),
            'has_center_line': 'center' in self.lanes,
            'roi_configured': self.roi_vertices is not None
        }


def create_lane_detector(
    roi_vertices: Optional[np.ndarray] = None
) -> LaneDetector:
    """Factory function para crear detector de carriles"""
    return LaneDetector(roi_vertices=roi_vertices)
