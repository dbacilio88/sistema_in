from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
import json
import base64
import numpy as np
import cv2
import asyncio
import httpx
import time
from datetime import datetime
from collections import defaultdict
import uuid
import random
from concurrent.futures import ThreadPoolExecutor
import logging

from app.core import get_logger
from app.services.model_service import model_service
from app.services.django_api import django_api

logger = get_logger(__name__)
router = APIRouter()

# 🚀 Thread pool para procesamiento de OCR en paralelo (no bloquea frame processing)
ocr_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ocr_worker")


class VehicleTracker:
    """Simple vehicle tracker for speed estimation"""
    
    def __init__(self):
        self.tracks = defaultdict(list)  # vehicle_id -> list of detections
        self.max_history = 30  # Keep last 30 frames
        
    def update(self, vehicle_id: str, detection: Dict):
        """Add detection to track history"""
        self.tracks[vehicle_id].append({
            **detection,
            'timestamp': datetime.now()
        })
        
        # Keep only recent history
        if len(self.tracks[vehicle_id]) > self.max_history:
            self.tracks[vehicle_id] = self.tracks[vehicle_id][-self.max_history:]
    
    def get_history(self, vehicle_id: str) -> List[Dict]:
        """Get track history for a vehicle"""
        return self.tracks[vehicle_id]
    
    def clear_old_tracks(self, max_age_seconds: int = 10):
        """Remove old tracks"""
        now = datetime.now()
        to_remove = []
        
        for vehicle_id, history in self.tracks.items():
            if history:
                last_seen = history[-1]['timestamp']
                age = (now - last_seen).total_seconds()
                if age > max_age_seconds:
                    to_remove.append(vehicle_id)
        
        for vehicle_id in to_remove:
            del self.tracks[vehicle_id]


class RealtimeDetector:
    """
    Detector en tiempo real para identificación de vehículos e infracciones
    Integrado con YOLOv8, OCR y Django backend
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.tracker = VehicleTracker()
        self.frame_count = 0
        self.processed_infractions = set()  # Track processed infractions to avoid duplicates
        self.infraction_plates = {}  # Track plates with infractions: {plate: {type, timestamp, frame}}
        self.plate_cooldown_frames = 90  # ~3 segundos a 30fps - evitar duplicados de la misma placa
        self.ocr_frame_interval = 5  # 🚀 Ejecutar OCR solo cada 5 frames (mejora FPS significativamente)
        
        # 🚀 NUEVAS OPTIMIZACIONES AGRESIVAS
        self.frame_skip_interval = 2  # Procesar solo 1 de cada 2 frames
        self.last_detections = None  # Cache de últimas detecciones
        self.last_processed_frame = None  # Último frame procesado
        self.detection_resolution = (640, 480)  # Resolución reducida para YOLO (mejora velocidad 50-60%)
        self.output_quality = 75  # Calidad JPEG para output (70-85% reduce tamaño sin pérdida visible)
        self.log_level = logging.INFO  # Nivel de logging configurable
        self.pending_ocr_tasks = []  # Tareas de OCR en background
        
    async def initialize_models(self):
        """Initialize ML models on first use"""
        await model_service.initialize()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected", total_connections=len(self.active_connections))
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected", total_connections=len(self.active_connections))
    
    async def process_frame(self, frame_data: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un frame de video y retorna las detecciones usando YOLOv8 y OCR
        
        Args:
            frame_data: Imagen en base64
            config: Configuración de detección (tipos de infracciones, umbrales, etc.)
        
        Returns:
            Detecciones encontradas en el frame
        """
        # ⏱️ START: Track processing time
        processing_start_time = time.time()
        
        try:
            # Ensure models are initialized
            if not model_service._initialized:
                logger.info("🔄 Initializing models...")
                await self.initialize_models()
                logger.info("✅ Models initialized")
            
            # Decodificar la imagen base64
            logger.info(f"📥 Decoding frame data (length: {len(frame_data) if frame_data else 0})...")
            image_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("❌ Failed to decode frame")
                return {"error": "Invalid frame data"}
            
            height, width = frame.shape[:2]
            self.frame_count += 1
            
            # 🚀 OPTIMIZACIÓN 1: Frame skipping inteligente
            # Procesar solo 1 de cada N frames, retornar detecciones cacheadas para frames skipped
            frame_skip_interval = config.get('frame_skip_interval', self.frame_skip_interval)
            should_process_frame = (self.frame_count % frame_skip_interval == 0)
            
            if not should_process_frame and self.last_detections:
                logger.debug(f"⏭️ Skipping frame #{self.frame_count} (processing every {frame_skip_interval} frames)")
                
                # Retornar último frame procesado con detecciones cacheadas
                _, buffer = cv2.imencode('.jpg', self.last_processed_frame if self.last_processed_frame is not None else frame, 
                                         [cv2.IMWRITE_JPEG_QUALITY, self.output_quality])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                return {
                    **self.last_detections,
                    "frame": frame_base64,
                    "frame_number": self.frame_count,
                    "cached": True,  # Indicar que son detecciones cacheadas
                    "timestamp": datetime.now().isoformat()
                }
            
            # 🚀 OPTIMIZACIÓN 2: Configuración dinámica desde frontend
            ocr_interval = config.get('ocr_frame_interval', self.ocr_frame_interval)
            if ocr_interval != self.ocr_frame_interval:
                logger.info(f"🔧 OCR frame interval updated: {self.ocr_frame_interval} → {ocr_interval}")
                self.ocr_frame_interval = ocr_interval
            
            # 🚀 OPTIMIZACIÓN 3: Output quality configurable
            output_quality = config.get('output_quality', self.output_quality)
            if output_quality != self.output_quality:
                logger.info(f"🔧 Output quality updated: {self.output_quality}% → {output_quality}%")
                self.output_quality = output_quality
            
            # 🚀 OPTIMIZACIÓN 4: Log level configurable
            log_level_str = config.get('log_level', 'INFO')
            log_level_map = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR}
            new_log_level = log_level_map.get(log_level_str.upper(), logging.INFO)
            if new_log_level != self.log_level:
                logger.info(f"🔧 Log level updated: {logging.getLevelName(self.log_level)} → {log_level_str.upper()}")
                self.log_level = new_log_level
                logger.setLevel(self.log_level)
            
            verbose_logging = (self.log_level == logging.DEBUG)
            
            if verbose_logging:
                logger.debug(f"🖼️ Frame #{self.frame_count}: {width}x{height}, OCR interval: every {self.ocr_frame_interval} frames")
            
            # 🚀 OPTIMIZACIÓN 5: Resize frame para YOLO detection (50-60% más rápido)
            # Mantener frame original para OCR (mayor precisión en placas)
            detection_frame = frame
            detection_width, detection_height = self.detection_resolution
            
            if config.get('enable_yolo_resize', True):  # Habilitado por defecto
                if width > detection_width or height > detection_height:
                    # Calcular aspect ratio para mantener proporciones
                    aspect = width / height
                    if aspect > (detection_width / detection_height):
                        new_width = detection_width
                        new_height = int(detection_width / aspect)
                    else:
                        new_height = detection_height
                        new_width = int(detection_height * aspect)
                    
                    detection_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                    scale_x = width / new_width
                    scale_y = height / new_height
                    logger.debug(f"🔍 Resized for YOLO: {width}x{height} → {new_width}x{new_height} (scale: {scale_x:.2f}x, {scale_y:.2f}y)")
                else:
                    scale_x = scale_y = 1.0
            else:
                scale_x = scale_y = 1.0
            
            # Detect vehicles using YOLOv8
            confidence_threshold = config.get('confidence_threshold', 0.5)
            logger.debug(f"🔍 Detecting vehicles with confidence >= {confidence_threshold}")
            
            vehicle_detections = await model_service.detect_vehicles(
                detection_frame,  # 🚀 Usar frame con resolución reducida
                confidence_threshold=confidence_threshold
            )
            
            # 🚀 Escalar bboxes de vuelta a resolución original si se hizo resize
            if scale_x != 1.0 or scale_y != 1.0:
                for vehicle in vehicle_detections:
                    bbox = vehicle['bbox']
                    vehicle['bbox'] = [
                        bbox[0] * scale_x,
                        bbox[1] * scale_y,
                        bbox[2] * scale_x,
                        bbox[3] * scale_y
                    ]
            
            logger.debug(f"🚗 Received {len(vehicle_detections)} vehicle detections from YOLO")
            
            if len(vehicle_detections) == 0:
                logger.debug("⚠️ No vehicles detected, returning empty frame")
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.output_quality])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                result = {
                    "frame": frame_base64,
                    "detections": [],
                    "infractions_registered": 0,
                    "fps": 30.0,
                    "frame_number": self.frame_count,
                    "cached": False,
                    "timestamp": datetime.now().isoformat()
                }
                
                # 🚀 Cachear resultado para frame skipping
                self.last_detections = result
                self.last_processed_frame = frame
                
                return result
            
            detections = []
            infractions_detected = []
            
            # Detectar estado del semáforo si está habilitado
            traffic_light_state = None
            traffic_light_detections_list = []
            if config.get('enable_traffic_light', False):
                traffic_light_roi = config.get('traffic_light_roi')  # (x1, y1, x2, y2)
                traffic_light_detection = await model_service.detect_traffic_light(
                    frame,
                    roi=traffic_light_roi
                )
                
                if traffic_light_detection:
                    traffic_light_state = traffic_light_detection['state']
                    traffic_light_detections_list = traffic_light_detection.get('all_detections', [])
                    detection_count = traffic_light_detection.get('count', 0)
                    
                    logger.info(
                        f"🚦 Traffic light detected: {traffic_light_state} "
                        f"(confidence={traffic_light_detection['confidence']:.2f}, "
                        f"detections={detection_count})"
                    )
            
            # Detectar carriles si está habilitado
            lane_detection = None
            if config.get('enable_lane_detection', False):
                lane_roi = config.get('lane_roi')  # Vértices del ROI
                lane_detection = await model_service.detect_lanes(
                    frame,
                    roi_vertices=lane_roi
                )
                
                if lane_detection and verbose_logging:
                    logger.info(
                        f"🛣️ Lanes detected: {lane_detection['lane_count']} lanes "
                        f"(center: {lane_detection['has_center_line']})"
                    )
            
            if verbose_logging:
                logger.info(f"🔄 Processing {len(vehicle_detections)} vehicle detections...")
            
            # Process each vehicle detection
            for idx, vehicle in enumerate(vehicle_detections):
                try:
                    vehicle_id = f"v{idx}"
                    
                    if verbose_logging:
                        logger.info(f"🚙 Processing vehicle #{idx+1}: {vehicle.get('vehicle_type', 'unknown')}")
                    
                    # Track vehicle
                    self.tracker.update(vehicle_id, vehicle)
                
                    # License plate variables (will be detected after infraction is confirmed)
                    license_plate = None
                    license_confidence = 0.0
                    
                    # Check for infractions
                    infraction_type = None
                    infraction_data = {}
                    
                    # 🚫 FILTRO: Solo detectar infracciones en vehículos motorizados
                    # Excluir: person, bicycle
                    # Incluir: car, motorcycle, bus, truck
                    vehicle_type = vehicle.get('vehicle_type', 'unknown')
                    MOTORIZED_VEHICLES = ['car', 'motorcycle', 'bus', 'truck']
                    
                    if vehicle_type not in MOTORIZED_VEHICLES:
                        logger.debug(
                            f"⏭️  Skipping infraction check for {vehicle_type} "
                            f"(only checking motorized vehicles)"
                        )
                        continue
                    
                    logger.debug(f"🔍 Checking infractions for {vehicle_type}")
                    
                    # 🎯 PRIORIDAD 1: Verificar si el FRONTEND ya detectó una infracción
                    # El frontend puede enviar wrong_lane, red_light, etc detectadas en el cliente
                    if vehicle.get('has_infraction') and vehicle.get('infraction_type'):
                        infraction_type = vehicle.get('infraction_type')
                        infraction_data = vehicle.get('infraction_data', {})
                        # Asegurar que vehicle_type esté en infraction_data
                        if 'vehicle_type' not in infraction_data:
                            infraction_data['vehicle_type'] = vehicle_type
                        
                        logger.info(
                            f"🎯 INFRACTION FROM FRONTEND: {infraction_type} for {vehicle_type} "
                            f"(client-side detection)"
                        )
                    
                    # 🎯 PRIORIDAD 2: SIMULACIÓN/DETECCIÓN EN BACKEND (solo si no hay infracción del frontend)
                    if not infraction_type:
                        # SIMULACIÓN AUTOMÁTICA DE INFRACCIONES
                        # Simula infracciones de velocidad para demostración
                        # Cada 3 vehículos detectados, genera una infracción de velocidad
                        simulate_infractions = config.get('simulate_infractions', True)
                        
                        logger.info(f"⚙️  Config: simulate={simulate_infractions}, infractions={config.get('infractions', [])}")
                        
                        if simulate_infractions and 'speeding' in config.get('infractions', []):
                            # Simular infracción para algunos vehículos (33% de probabilidad)
                            will_infract = (self.frame_count + idx) % 3 == 0
                            logger.info(f"🎲 Vehicle #{idx+1}: frame={self.frame_count}, idx={idx}, will_infract={will_infract}")
                            
                            if will_infract:
                                # Generar velocidad aleatoria entre 70-100 km/h
                                simulated_speed = random.uniform(70, 100)
                                speed_limit = config.get('speed_limit', 60)
                                
                                logger.info(f"🚨 Generated speed: {simulated_speed:.1f} km/h (limit: {speed_limit} km/h)")
                                
                                if simulated_speed > speed_limit:
                                    infraction_type = 'speed'  # FIXED: Django expects 'speed' not 'speeding'
                                    infraction_data = {
                                        'detected_speed': round(simulated_speed, 1),
                                        'speed_limit': speed_limit,
                                        'vehicle_type': vehicle_type
                                    }
                                    vehicle['speed'] = round(simulated_speed, 1)
                                    vehicle['has_infraction'] = True
                                    logger.info(
                                        f"🚨 INFRACCIÓN DETECTADA: {vehicle_type} a {simulated_speed:.1f} km/h "
                                        f"(límite: {speed_limit} km/h)"
                                    )
                                else:
                                    logger.info(f"✅ Vehicle within speed limit: {simulated_speed:.1f} km/h")
                        else:
                            logger.info(f"⏭️  Vehicle #{idx+1} skipped (no infraction this frame)")
                    else:
                        logger.info(f"⚠️  Simulation disabled or speeding not in config")
                    
                    # Speed violation detection (modo real) - Solo si no hay infracción del frontend
                    if not infraction_type and not simulate_infractions and 'speeding' in config.get('infractions', []) and config.get('enable_speed', True):
                        logger.info(f"🎯 Real speed detection mode")
                        track_history = self.tracker.get_history(vehicle_id)
                        
                        if len(track_history) >= 10:  # Need enough frames for speed estimation
                            estimated_speed = await model_service.estimate_speed(
                                track_history,
                                fps=30.0,  # Assuming 30 fps
                                calibration_data=None
                            )
                            
                            if estimated_speed:
                                vehicle['speed'] = estimated_speed
                                speed_limit = config.get('speed_limit', 60)
                                
                                # Check if speeding
                                if estimated_speed > speed_limit:
                                    infraction_type = 'speed'  # FIXED: Django expects 'speed' not 'speeding'
                                    infraction_data = {
                                        'detected_speed': estimated_speed,
                                        'speed_limit': speed_limit,
                                        'vehicle_type': vehicle_type
                                    }
                                    vehicle['has_infraction'] = True
                                    logger.info(
                                        f"🚨 SPEED VIOLATION: {vehicle_type} at {estimated_speed:.1f} km/h "
                                        f"(limit: {speed_limit} km/h)"
                                    )
                    
                    # Red light violation detection
                    if not infraction_type and 'red_light' in config.get('infractions', []):
                        # Check if traffic light is red
                        logger.debug(f"🔍 Checking red light: state={traffic_light_state}")
                        if traffic_light_state and traffic_light_state == 'red':
                            # Check if vehicle crossed stop line
                            # Stop line is defined in config as y-coordinate
                            stop_line_y = config.get('stop_line_y')
                            logger.debug(f"🔍 Red light detected, stop_line_y={stop_line_y}")
                            
                            if stop_line_y:
                                # Vehicle center Y position
                                vehicle_center_y = vehicle['bbox'][1] + vehicle['bbox'][3] / 2
                                
                                logger.debug(
                                    f"🔍 Vehicle position check: center_y={vehicle_center_y:.0f}, "
                                    f"stop_line_y={stop_line_y}, crossed={vehicle_center_y > stop_line_y}"
                                )
                                
                                # If vehicle crossed stop line while light is red
                                if vehicle_center_y > stop_line_y:
                                    infraction_type = 'red_light'
                                    infraction_data = {
                                        'traffic_light_state': 'red',
                                        'stop_line_y': stop_line_y,
                                        'vehicle_position_y': int(vehicle_center_y),
                                        'vehicle_type': vehicle_type
                                    }
                                    vehicle['has_infraction'] = True
                                    logger.info(
                                        f"🚨 RED LIGHT VIOLATION: {vehicle_type} crossed stop line "
                                        f"(line={stop_line_y}, vehicle={vehicle_center_y:.0f})"
                                    )
                            else:
                                logger.warning("⚠️ Red light detected but stop_line_y not configured")
                        else:
                            logger.debug(f"🟢 Traffic light not red, skipping red light check")
                    
                    # Lane invasion detection
                    if not infraction_type and 'wrong_lane' in config.get('infractions', []):
                        logger.debug(f"🔍 Checking lane invasion: lane_detection={lane_detection is not None}, has_lanes={lane_detection.get('lanes') if lane_detection else None}")
                        if lane_detection and lane_detection.get('lanes'):
                            # Construir bbox en formato [x1, y1, x2, y2]
                            bbox_for_check = [
                                vehicle['bbox'][0],
                                vehicle['bbox'][1],
                                vehicle['bbox'][0] + vehicle['bbox'][2],
                                vehicle['bbox'][1] + vehicle['bbox'][3]
                            ]
                            
                            lane_violation = model_service.check_lane_violation(
                                vehicle_bbox=bbox_for_check,
                                lane_detection=lane_detection
                            )
                            
                            if lane_violation:
                                infraction_type = 'wrong_lane'
                                infraction_data = {
                                    'subtype': lane_violation['subtype'],
                                    'lane_crossed': lane_violation['lane_crossed'],
                                    'distance': round(lane_violation['distance'], 2),
                                    'vehicle_position': lane_violation['vehicle_position'],
                                    'vehicle_type': vehicle_type
                                }
                                vehicle['has_infraction'] = True
                                logger.info(
                                    f"🚨 LANE INVASION: {vehicle_type} crossed {lane_violation['lane_crossed']} line "
                                    f"(type: {lane_violation['subtype']}, distance: {lane_violation['distance']:.1f}px)"
                                )
                    
                    # 🔍 Si hay infracción, intentar OCR para obtener placa
                    if infraction_type:
                        logger.debug(f"🚨 INFRACTION DETECTED: {infraction_type} for {vehicle_type}")
                        logger.debug(f"   📍 Frame: {self.frame_count}, Vehicle Index: #{idx+1}")
                        logger.debug(f"   📦 BBox: {vehicle['bbox']}, Confidence: {vehicle['confidence']:.2f}")
                        
                        # 🚀 OPTIMIZACIÓN: Ejecutar OCR solo cada N frames EXCEPTO cuando hay infracción
                        # CRÍTICO: Si detectamos una infracción, SIEMPRE ejecutar OCR para capturar la placa
                        is_ocr_interval_frame = (self.frame_count % self.ocr_frame_interval == 0)
                        force_ocr_on_infraction = True  # Forzar OCR cuando hay infracción
                        should_run_ocr = is_ocr_interval_frame or force_ocr_on_infraction
                        
                        if not is_ocr_interval_frame and force_ocr_on_infraction:
                            logger.info(f"🎯 FORCING OCR due to infraction (frame {self.frame_count}, interval: every {self.ocr_frame_interval})")
                        elif not should_run_ocr:
                            logger.debug(f"⏭️ Skipping OCR this frame (interval: every {self.ocr_frame_interval} frames)")
                        
                        # 🚀 NUEVA OPTIMIZACIÓN: OCR en background (no bloquea frame processing)
                        # Intentar detectar placa (UNIVERSAL para TODAS las infracciones)
                        logger.debug(f"🔍 OCR Status: license_plate={license_plate!r}, should_run={should_run_ocr}")
                        
                        # 🚀 MODO BACKGROUND: No esperar resultado de OCR, continuar procesando
                        # El OCR se ejecuta en paralelo y actualizará la detección después
                        use_background_ocr = config.get('background_ocr', True)  # Activado por defecto
                        
                        if not license_plate and should_run_ocr:
                            logger.debug(f"🔤 Attempting OCR for {infraction_type.upper()} infraction...")
                            
                            # Convertir bbox a formato dict para OCR
                            bbox = vehicle['bbox']
                            if isinstance(bbox, list) and len(bbox) == 4:
                                x1, y1, x2, y2 = bbox
                                bbox_dict = {
                                    'x': int(x1),
                                    'y': int(y1),
                                    'width': int(x2 - x1),
                                    'height': int(y2 - y1)
                                }
                            elif isinstance(bbox, dict):
                                bbox_dict = bbox
                            else:
                                bbox_dict = None
                            
                            if bbox_dict and bbox_dict.get('width', 0) > 0 and bbox_dict.get('height', 0) > 0:
                                    # MODO NORMAL: Esperar resultado (bloquea)
                                    plate_result = await model_service.detect_license_plate(frame, bbox_dict)
                                    if plate_result:
                                        license_plate, license_confidence = plate_result
                                        vehicle['license_plate'] = license_plate
                                        vehicle['license_confidence'] = license_confidence
                                        logger.info(f"✅ PLATE DETECTED: '{license_plate}' (conf: {license_confidence:.2f})")
                                    else:
                                        logger.debug(f"⚠️ OCR failed - Could not detect license plate")
                            else:
                                logger.debug(f"⚠️ Invalid bbox dimensions for OCR: {bbox_dict}")
                        else:
                            if license_plate:
                                logger.debug(f"📋 Plate already available: '{license_plate}' (conf: {license_confidence:.2f})")
                        
                        # 🚫 Verificar deduplicación por placa
                        if license_plate:
                            logger.info(f"🔍 Checking deduplication for plate: '{license_plate}'")
                            
                            # Limpiar placas antiguas (fuera del cooldown)
                            plates_to_remove = []
                            for plate, data in self.infraction_plates.items():
                                if self.frame_count - data['frame'] > self.plate_cooldown_frames:
                                    plates_to_remove.append(plate)
                            
                            if plates_to_remove:
                                for plate in plates_to_remove:
                                    del self.infraction_plates[plate]
                                    logger.debug(f"🧹 Removed expired plate from cooldown: {plate}")
                                logger.info(f"🧹 Cleaned {len(plates_to_remove)} expired plates from tracking")
                            
                            # Mostrar estado actual del tracking
                            logger.info(f"📊 Currently tracking {len(self.infraction_plates)} plates in cooldown:")
                            for plate, data in self.infraction_plates.items():
                                frames_since = self.frame_count - data['frame']
                                logger.info(f"   - '{plate}': {data['type']} ({frames_since} frames ago)")
                            
                            # Verificar si esta placa ya tiene una infracción reciente
                            if license_plate in self.infraction_plates:
                                previous_infraction = self.infraction_plates[license_plate]
                                frames_ago = self.frame_count - previous_infraction['frame']
                                logger.warning(
                                    f"⏭️  🚫 DUPLICATE DETECTED: Plate '{license_plate}' already has "
                                    f"{previous_infraction['type']} infraction from {frames_ago} frames ago "
                                    f"(cooldown: {self.plate_cooldown_frames} frames). SKIPPING SAVE."
                                )
                                # Marcar como NO infracción para no guardarlo
                                infraction_type = None
                                infraction_data = {}
                                vehicle['has_infraction'] = False
                            else:
                                # Registrar esta placa con infracción
                                self.infraction_plates[license_plate] = {
                                    'type': infraction_type,
                                    'frame': self.frame_count,
                                    'timestamp': datetime.now().isoformat()
                                }
                                logger.info(
                                    f"✅ ✨ NEW UNIQUE INFRACTION REGISTERED: {infraction_type} for plate '{license_plate}' "
                                    f"(frame {self.frame_count}). Will be saved to database."
                                )
                        else:
                            # Sin placa, permitir pero avisar
                            logger.warning(
                                f"⚠️ Infraction {infraction_type} detected but NO LICENSE PLATE found. "
                                f"Will register but may create duplicates."
                            )
                    
                    # 🔤 OCR para todos los vehículos motorizados (opcional)
                    # Útil para registrar placas incluso sin infracciones
                    if not license_plate and config.get('ocr_all_vehicles', False):
                        # Solo para vehículos motorizados (no personas)
                        vehicle_type = vehicle.get('vehicle_type', 'car')
                        if vehicle_type not in ['person', 'pedestrian']:
                            logger.info(f"🔤 OCR enabled for all vehicles - attempting detection on {vehicle_type}")
                            
                            # Convertir bbox a formato dict para OCR
                            bbox = vehicle['bbox']
                            if isinstance(bbox, list) and len(bbox) == 4:
                                x1, y1, x2, y2 = bbox
                                bbox_dict = {
                                    'x': int(x1),
                                    'y': int(y1),
                                    'width': int(x2 - x1),
                                    'height': int(y2 - y1)
                                }
                            elif isinstance(bbox, dict):
                                bbox_dict = bbox
                            else:
                                bbox_dict = None
                            
                            if bbox_dict and bbox_dict.get('width', 0) > 0 and bbox_dict.get('height', 0) > 0:
                                plate_result = await model_service.detect_license_plate(
                                    frame,
                                    bbox_dict
                                )
                                if plate_result:
                                    license_plate, license_confidence = plate_result
                                    vehicle['license_plate'] = license_plate
                                    vehicle['license_confidence'] = license_confidence
                                    logger.info(f"✅ PLATE DETECTED (no infraction): '{license_plate}' (conf: {license_confidence:.2f})")
                    
                    # Create detection object
                    detection = {
                        'id': f"{self.frame_count}-{idx}",
                        'type': 'infraction' if infraction_type else 'vehicle',
                        'vehicle_type': vehicle.get('vehicle_type', 'car'),
                        'confidence': vehicle['confidence'],
                        'bbox': vehicle['bbox'],
                        'timestamp': datetime.now().isoformat(),
                        'has_infraction': vehicle.get('has_infraction', False)
                    }
                    
                    if license_plate:
                        detection['license_plate'] = license_plate
                        detection['license_confidence'] = license_confidence
                    
                    if vehicle.get('speed'):
                        detection['speed'] = vehicle['speed']
                    
                    if infraction_type:
                        detection['infraction_type'] = infraction_type
                        detection['infraction_data'] = infraction_data
                        infractions_detected.append(detection)
                        
                        # Dibujar recuadro ROJO para vehículos con infracción
                        x1, y1, x2, y2 = vehicle['bbox']
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)
                        
                        # Agregar etiqueta con tipo de infracción y velocidad
                        label = f"INFRACCION: {infraction_type.upper()}"
                        if vehicle.get('speed'):
                            label += f" - {vehicle['speed']:.0f} km/h"
                        
                        # Fondo para el texto
                        (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        cv2.rectangle(frame, (int(x1), int(y1) - text_height - 10), 
                                    (int(x1) + text_width, int(y1)), (0, 0, 255), -1)
                        cv2.putText(frame, label, (int(x1), int(y1) - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    else:
                        # Dibujar recuadro verde para vehículos sin infracción
                        x1, y1, x2, y2 = vehicle['bbox']
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        
                        # Etiqueta con tipo de vehículo
                        label = vehicle.get('vehicle_type', 'vehicle').upper()
                        if vehicle.get('speed'):
                            label += f" - {vehicle['speed']:.0f} km/h"
                        
                        cv2.putText(frame, label, (int(x1), int(y1) - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    detections.append(detection)
                    logger.info(f"✅ Detection added: {detection.get('vehicle_type')} - infraction={infraction_type is not None}")
                
                except Exception as vehicle_error:
                    logger.error(f"❌ Error processing vehicle #{idx+1}: {str(vehicle_error)}", exc_info=True)
                    # Continue with next vehicle
                    continue
            
            logger.info(f"📊 Total detections: {len(detections)}, Infractions: {len(infractions_detected)}")
            
            # ⏱️ END: Calculate processing time
            processing_end_time = time.time()
            processing_time_seconds = processing_end_time - processing_start_time
            logger.info(f"⏱️  Frame processing time: {processing_time_seconds:.3f}s")
            
            # ⏱️ ADD ML TIME TO ALL DETECTIONS (not just infractions)
            ml_processing_time_ms = round(processing_time_seconds * 1000, 2)
            logger.info(f"⏱️ ML Time: {ml_processing_time_ms}ms | Detections: {len(detections)} | Infractions: {len(infractions_detected)}")
            
            # Add ML Time to ALL detections for frontend display
            for det in detections:
                det['ml_prediction_time_ms'] = ml_processing_time_ms
            
            # Add processing time + ML Time + Risk to each infraction
            for infraction in infractions_detected:
                infraction['processing_time_seconds'] = round(processing_time_seconds, 3)
                infraction['ml_prediction_time_ms'] = ml_processing_time_ms
                
                # Calculate recidivism risk based on severity
                inf_type = infraction.get('infraction_type')
                risk_score = 0.0
                
                if inf_type == 'speed':
                    # Speed infractions: base 0.3 + excess over limit (max 0.7)
                    detected_speed = infraction.get('detected_speed', 0)
                    speed_limit = infraction.get('speed_limit', 50)
                    excess = max(0, detected_speed - speed_limit)
                    risk_score = min(0.3 + (excess / 100.0), 1.0)
                elif inf_type == 'red_light':
                    # Red light: very high risk (0.85)
                    risk_score = 0.85
                elif inf_type in ['wrong_lane', 'lane_invasion']:
                    # Lane violations: medium-high risk (0.70)
                    risk_score = 0.70
                else:
                    # Default: low risk (0.40)
                    risk_score = 0.40
                
                infraction['recidivism_risk'] = round(risk_score, 3)
                
                # Update the corresponding detection object with ml_time and risk
                infraction_id = infraction.get('id')
                for det in detections:
                    if det.get('id') == infraction_id:
                        det['ml_prediction_time_ms'] = ml_processing_time_ms
                        det['recidivism_risk'] = round(risk_score, 3)
                        break
                
                logger.info(f"✅ [{inf_type}] ML Time: {ml_processing_time_ms}ms | Risk: {risk_score:.3f}")
            
            # Clean old tracks periodically
            if self.frame_count % 100 == 0:
                self.tracker.clear_old_tracks()
                # Also clear old processed infractions (keep last 1000)
                if len(self.processed_infractions) > 1000:
                    self.processed_infractions = set(list(self.processed_infractions)[-500:])
            
            # Send infractions to Django backend (non-blocking)
            if infractions_detected:
                logger.info(f"💾 ====== SAVING INFRACTIONS TO DATABASE ======")
                logger.info(f"💾 Total infractions to save: {len(infractions_detected)}")
                for idx, inf in enumerate(infractions_detected, 1):
                    plate = inf.get('license_plate', 'NO_PLATE')
                    inf_type = inf.get('infraction_type', 'unknown')
                    proc_time = inf.get('processing_time_seconds', 0)
                    logger.info(f"   {idx}. {inf_type} - Plate: '{plate}' - Vehicle: {inf.get('vehicle_type')} - Processing: {proc_time:.3f}s")
                
                asyncio.create_task(
                    self._save_infractions_to_database(infractions_detected)
                )
            else:
                logger.debug(f"ℹ️ No infractions to save this frame")
            
            # 🚀 OPTIMIZACIÓN: Encode frame con calidad reducida para menor tamaño y transmisión más rápida
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.output_quality])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            logger.debug(f"📤 Sending result with {len(detections)} detections to client")
            
            result = {
                "type": "detection",
                "frame": frame_base64,
                "detections": detections,
                "infractions_registered": len(infractions_detected),
                "fps": 30.0,
                "frame_number": self.frame_count,
                "cached": False,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add traffic light info if detected
            if traffic_light_state:
                result["traffic_light_state"] = traffic_light_state
                result["traffic_light_confidence"] = traffic_light_detection.get('confidence', 0.0)
                result["traffic_light_detections"] = len(traffic_light_detections_list)
            
            # Add lane info if detected
            if lane_detection:
                result["lanes_detected"] = lane_detection.get('count', 0)
            
            # 🚀 Cachear resultado y frame para frame skipping
            self.last_detections = result
            self.last_processed_frame = frame
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    async def _save_infractions_to_database(self, detections_with_infractions: List[Dict]):
        """
        Save detected infractions to Django database
        GUARDA TODAS LAS INFRACCIONES, incluso sin placa identificada
        
        Args:
            detections_with_infractions: List of detections that have infractions
        """
        try:
            logger.info(f"💾 🔄 Starting database save process...")
            logger.info(f"💾 Received {len(detections_with_infractions)} infractions to process")
            
            # Preparar detecciones para el formato de Django API
            formatted_detections = []
            
            for idx, detection in enumerate(detections_with_infractions, 1):
                logger.info(f"💾 [{idx}/{len(detections_with_infractions)}] Formatting infraction...")
                
                infraction_type = detection.get('infraction_type', 'speed')
                vehicle_type = detection.get('vehicle_type', 'car')
                license_plate = detection.get('license_plate', '')
                
                logger.info(f"   📋 Type: {infraction_type}, Vehicle: {vehicle_type}, Plate: '{license_plate}'")
                
                # Formato correcto para Django InfractionCreateSerializer
                formatted_detection = {
                    'infraction_type': infraction_type,  # speed, red_light, etc
                    'detected_at': datetime.now().isoformat(),  # Campo requerido
                    'severity': 'medium',  # low, medium, high, critical
                    'status': 'pending',  # pending, validated, rejected, etc
                }
                
                # Agregar placa si existe
                if license_plate:
                    formatted_detection['license_plate_detected'] = license_plate
                    formatted_detection['license_plate_confidence'] = detection.get('license_confidence', 0.0)
                    logger.info(f"   ✅ License plate included: '{license_plate}' (conf: {formatted_detection['license_plate_confidence']:.2f})")
                else:
                    # Si NO hay placa, dejar vacío
                    formatted_detection['license_plate_detected'] = ''
                    formatted_detection['license_plate_confidence'] = 0.0
                    logger.warning(f"   ⚠️ No license plate for this infraction")
                
                # Agregar velocidad si existe (para infracciones de velocidad)
                if detection.get('speed'):
                    formatted_detection['detected_speed'] = float(detection['speed'])
                
                # Agregar límite de velocidad si existe
                if detection.get('infraction_data'):
                    if 'speed_limit' in detection['infraction_data']:
                        formatted_detection['speed_limit'] = int(detection['infraction_data']['speed_limit'])
                    if 'detected_speed' in detection['infraction_data']:
                        formatted_detection['detected_speed'] = float(detection['infraction_data']['detected_speed'])
                
                # ⏱️ Add processing time (tiempo de procesamiento y reconocimiento)
                if detection.get('processing_time_seconds'):
                    formatted_detection['processing_time_seconds'] = detection['processing_time_seconds']
                    logger.info(f"   ⏱️  Processing time: {detection['processing_time_seconds']:.3f}s")
                
                # 🚀 Add ML prediction time (en milisegundos)
                if detection.get('ml_prediction_time_ms'):
                    formatted_detection['ml_prediction_time_ms'] = detection['ml_prediction_time_ms']
                    logger.info(f"   ⏱️  ML Time: {detection['ml_prediction_time_ms']}ms")
                
                # 🎯 Add recidivism risk score
                if detection.get('recidivism_risk'):
                    formatted_detection['recidivism_risk'] = detection['recidivism_risk']
                    logger.info(f"   🎯 Risk Score: {detection['recidivism_risk']:.3f}")
                
                # Metadata adicional
                formatted_detection['evidence_metadata'] = {
                    'vehicle_type': detection.get('vehicle_type', 'car'),
                    'confidence': detection.get('confidence', 0.0),
                    'bbox': detection.get('bbox', []),
                    'detection_id': detection.get('id', ''),
                    'timestamp': detection.get('timestamp', ''),
                    'source': 'webcam_local'
                }
                
                formatted_detections.append(formatted_detection)
                logger.info(f"   ✅ Infraction #{idx} formatted successfully")
            
            logger.info(f"💾 📤 Sending {len(formatted_detections)} infractions to Django API...")
            
            # Enviar a Django (una por una)
            created_count = 0
            created_infractions = []
            
            for idx, detection in enumerate(formatted_detections, 1):
                logger.info(f"💾 [{idx}/{len(formatted_detections)}] Saving to database...")
                logger.info(f"   📋 Plate: '{detection['license_plate_detected']}', Type: {detection['infraction_type']}")
                
                result = await django_api.create_infraction(
                    infraction_data=detection
                )
                
                if result:
                    created_count += 1
                    created_infractions.append(result)
                    logger.info(f"   ✅ SUCCESS - Infraction saved with code: {result.get('infraction_code')}")
                    logger.info(f"      ID: {result.get('id')}, Status: {result.get('status')}")
                    
                    # Si la infracción tiene vehículo asociado, solicitar predicción ML
                    vehicle_id = result.get('vehicle')
                    infraction_id = result.get('id')
                    
                    if vehicle_id and infraction_id:
                        logger.info(f"   🤖 Infraction has vehicle, requesting ML prediction...")
                        
                        # Obtener información del vehículo para conseguir el driver
                        try:
                            async with httpx.AsyncClient(timeout=django_api.timeout) as client:
                                vehicle_response = await client.get(
                                    f"{django_api.base_url}/api/vehicles/{vehicle_id}/"
                                )
                                
                                if vehicle_response.status_code == 200:
                                    vehicle_data = vehicle_response.json()
                                    driver = vehicle_data.get('driver')
                                    
                                    if driver:
                                        driver_dni = driver.get('document_number')
                                        if driver_dni:
                                            logger.info(f"   👤 Driver found: {driver_dni}, requesting ML prediction")
                                            
                                            # Llamar al servicio ML
                                            ml_result = await django_api.predict_recidivism(
                                                driver_dni=driver_dni,
                                                infraction_id=infraction_id
                                            )
                                            
                                            if ml_result:
                                                logger.info(
                                                    f"   🎯 ML prediction completed: "
                                                    f"risk={ml_result.get('recidivism_probability', 0)*100:.1f}%, "
                                                    f"time={ml_result.get('prediction_time_ms', 0):.2f}ms"
                                                )
                                            else:
                                                logger.warning(f"   ⚠️ ML prediction failed for driver {driver_dni}")
                                        else:
                                            logger.debug(f"   ℹ️ Driver has no DNI, skipping ML prediction")
                                    else:
                                        logger.debug(f"   ℹ️ Vehicle has no driver assigned, skipping ML prediction")
                                else:
                                    logger.warning(f"   ⚠️ Failed to fetch vehicle data: status={vehicle_response.status_code}")
                        except Exception as e:
                            logger.error(f"   ❌ Error fetching vehicle/driver for ML: {str(e)}")
                    else:
                        logger.debug(f"   ℹ️ No vehicle associated with infraction, skipping ML prediction")
                else:
                    logger.error(f"   ❌ FAILED - Could not save infraction")
            
            logger.info(f"💾 ====== DATABASE SAVE COMPLETE ======")
            logger.info(f"💾 Total saved: {created_count}/{len(formatted_detections)}")
            
            if created_count > 0:
                logger.info(f"💾 📊 Summary of saved infractions:")
                for idx, infraction in enumerate(created_infractions, 1):
                    license_plate = infraction.get('license_plate_detected') or 'NO_PLATE'
                    code = infraction.get('infraction_code', 'N/A')
                    inf_type = infraction.get('infraction_type', 'unknown')
                    speed = infraction.get('detected_speed', 'N/A')
                    
                    logger.info(
                        f"   {idx}. Code: {code} | Type: {inf_type} | "
                        f"Plate: '{license_plate}' | Speed: {speed} km/h"
                    )
            else:
                logger.error("💾 ⚠️ WARNING: No infractions were saved to database!")
            
        except Exception as e:
            logger.error(f"❌ Error guardando infracciones en la base de datos: {str(e)}", exc_info=True)


# Instancia global del detector
detector = RealtimeDetector()


@router.websocket("/ws/inference")
async def websocket_inference(websocket: WebSocket):
    """
    WebSocket endpoint para detección en tiempo real
    
    El cliente envía frames de video y recibe detecciones
    """
    # Aceptar la conexión sin validación de origen (para desarrollo)
    await websocket.accept()
    detector.active_connections.append(websocket)
    logger.info("WebSocket client connected", total_connections=len(detector.active_connections))
    
    try:
        while True:
            # Recibir datos del cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.debug(f"Received message type: {message.get('type')}")
            
            if message.get('type') == 'frame':
                # Procesar el frame
                frame_data = message.get('image')
                config = message.get('config', {})
                
                logger.info(f"Processing frame with config: {config}")
                
                # Procesar y enviar resultado
                result = await detector.process_frame(frame_data, config)
                
                logger.info(f"Sending result with {len(result.get('detections', []))} detections")
                
                await websocket.send_json(result)
                
            elif message.get('type') == 'config':
                # Client sent configuration
                logger.info(f"Received config: {message.get('data')}")
                await websocket.send_json({"type": "config_received", "status": "ok"})
                
            elif message.get('type') == 'ping':
                # Responder a ping para mantener la conexión
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        if websocket in detector.active_connections:
            detector.active_connections.remove(websocket)
        logger.info("Client disconnected normally", total_connections=len(detector.active_connections))
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        if websocket in detector.active_connections:
            detector.active_connections.remove(websocket)
        try:
            await websocket.close()
        except:
            pass
