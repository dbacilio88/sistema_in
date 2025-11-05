"""
Simplified Lane Detector for Inference Service

Detector ligero de carriles usando Hough Lines
"""

import logging
from typing import Optional, Tuple, Dict, Any, List
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class SimpleLaneDetector:
    """
    Detector simplificado de carriles usando Hough Transform
    
    Detecta líneas de carril y determina violaciones
    """
    
    def __init__(self, confidence_threshold: float = 0.6):
        self.confidence_threshold = confidence_threshold
        
        # Parámetros de detección
        self.canny_low = 50
        self.canny_high = 150
        self.hough_threshold = 50
        self.hough_min_line_length = 100
        self.hough_max_line_gap = 50
        
        # ROI por defecto (trapecio en mitad inferior)
        self.roi_vertices = None
        
        # Carriles detectados
        self.lanes = {}
        
        # Historial para suavizado
        self.lane_history = []
        self.max_history = 5
        
        logger.info("SimpleLaneDetector initialized")
    
    def set_roi(self, vertices: np.ndarray):
        """Configurar ROI"""
        self.roi_vertices = vertices
    
    def detect(
        self,
        frame: np.ndarray,
        roi_vertices: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Detectar carriles en el frame
        
        Args:
            frame: Frame BGR
            roi_vertices: Vértices del ROI (opcional)
            
        Returns:
            Dict con 'lanes', 'has_center_line', 'lane_count'
        """
        if roi_vertices is not None:
            self.roi_vertices = roi_vertices
        
        # Preprocesar
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, self.canny_low, self.canny_high)
        
        # Aplicar máscara ROI
        if self.roi_vertices is None:
            height, width = frame.shape[:2]
            self.roi_vertices = np.array([[
                (int(width * 0.1), height),
                (int(width * 0.4), int(height * 0.6)),
                (int(width * 0.6), int(height * 0.6)),
                (int(width * 0.9), height)
            ]], dtype=np.int32)
        
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, [self.roi_vertices], 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # Detectar líneas
        lines = cv2.HoughLinesP(
            masked_edges,
            rho=2,
            theta=np.pi/180,
            threshold=self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )
        
        # Clasificar líneas
        lanes = self._classify_lanes(lines, frame.shape)
        self.lanes = lanes
        
        return {
            'lanes': lanes,
            'has_center_line': 'center' in lanes,
            'lane_count': len(lanes),
            'confidence': 0.8 if lanes else 0.0
        }
    
    def _classify_lanes(
        self,
        lines: Optional[np.ndarray],
        frame_shape: Tuple[int, int, int]
    ) -> Dict[str, Dict[str, Any]]:
        """Clasificar líneas en carriles"""
        if lines is None:
            return {}
        
        height, width = frame_shape[:2]
        left_lines = []
        right_lines = []
        center_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            if x2 - x1 == 0:
                continue
            
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            
            # Filtrar horizontales
            if abs(slope) < 0.5:
                continue
            
            x_center = (x1 + x2) / 2
            
            if slope < 0 and x_center < width * 0.5:
                left_lines.append((slope, intercept, x1, y1, x2, y2))
            elif slope > 0 and x_center > width * 0.5:
                right_lines.append((slope, intercept, x1, y1, x2, y2))
            elif abs(x_center - width * 0.5) < width * 0.2:
                center_lines.append((slope, intercept, x1, y1, x2, y2))
        
        lanes = {}
        
        if left_lines:
            avg_slope = np.mean([s for s, _, _, _, _, _ in left_lines])
            avg_intercept = np.mean([i for _, i, _, _, _, _ in left_lines])
            lanes['left'] = {
                'slope': avg_slope,
                'intercept': avg_intercept,
                'side': 'left',
                'is_solid': True
            }
        
        if right_lines:
            avg_slope = np.mean([s for s, _, _, _, _, _ in right_lines])
            avg_intercept = np.mean([i for _, i, _, _, _, _ in right_lines])
            lanes['right'] = {
                'slope': avg_slope,
                'intercept': avg_intercept,
                'side': 'right',
                'is_solid': True
            }
        
        if center_lines:
            avg_slope = np.mean([s for s, _, _, _, _, _ in center_lines])
            avg_intercept = np.mean([i for _, i, _, _, _, _ in center_lines])
            lanes['center'] = {
                'slope': avg_slope,
                'intercept': avg_intercept,
                'side': 'center',
                'is_solid': True
            }
        
        return lanes
    
    def check_violation(
        self,
        vehicle_bbox: Tuple[float, float, float, float],
        lanes: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Verificar si vehículo está invadiendo carril
        
        Args:
            vehicle_bbox: [x1, y1, x2, y2] o [x, y, width, height]
            lanes: Carriles detectados (usa self.lanes si None)
            
        Returns:
            Dict con violación o None
        """
        lanes = lanes or self.lanes
        
        if not lanes:
            return None
        
        # Calcular centro del vehículo
        # Asumir formato [x1, y1, x2, y2]
        if len(vehicle_bbox) == 4:
            x1, y1, x2, y2 = vehicle_bbox
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
        else:
            return None
        
        # Verificar línea central (más crítico)
        if 'center' in lanes:
            center = lanes['center']
            if center['slope'] != 0:
                x_line = (y_center - center['intercept']) / center['slope']
                distance = abs(x_center - x_line)
                
                logger.debug(f"🔍 Center line: x_center={x_center:.1f}, x_line={x_line:.1f}, distance={distance:.1f}")
                
                # ✅ DETECCIÓN SIMPLIFICADA: Solo verificar proximidad
                if distance < 150:  # ✅ Aumentado threshold para resolución 480x272
                    logger.info(f"✅ CENTER line violation detected: distance={distance:.1f}px")
                    return {
                        'type': 'wrong_lane',
                        'subtype': 'center_line_violation',
                        'lane_crossed': 'center',
                        'distance': distance,
                        'vehicle_position': (int(x_center), int(y_center)),
                        'confidence': 0.9
                    }
        
        # Verificar líneas laterales
        for side in ['left', 'right']:
            if side in lanes:
                lane = lanes[side]
                if lane['slope'] != 0:
                    x_line = (y_center - lane['intercept']) / lane['slope']
                    distance = abs(x_center - x_line)
                    
                    logger.debug(f"🔍 Lane {side}: x_center={x_center:.1f}, x_line={x_line:.1f}, distance={distance:.1f}")
                    
                    # ✅ DETECCIÓN SIMPLIFICADA: Solo verificar si el vehículo está CERCA de la línea
                    # Sin importar de qué lado está (como en el test script exitoso)
                    threshold = 200  # ✅ Aumentado a 200px para video 480x272 (antes 50px no funcionaba)
                    
                    if distance < threshold:
                        subtype = f'crossed_{side}_line'
                        logger.info(f"✅ {side.upper()} line violation detected: distance={distance:.1f}px")
                        return {
                            'type': 'wrong_lane',
                            'subtype': subtype,
                            'lane_crossed': side,
                            'distance': distance,
                            'vehicle_position': (int(x_center), int(y_center)),
                            'confidence': 0.7
                        }
        
        return None
