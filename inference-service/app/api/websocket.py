from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import json
import base64
import numpy as np
import cv2
import asyncio
from datetime import datetime
from collections import defaultdict
import uuid
import random

from app.core import get_logger
from app.services.model_service import model_service
from app.services.django_api import django_api

logger = get_logger(__name__)
router = APIRouter()


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
            
            logger.info(f"🖼️  Frame #{self.frame_count}: {width}x{height}, config: {config}")
            
            # Detect vehicles using YOLOv8
            confidence_threshold = config.get('confidence_threshold', 0.5)  # Bajado a 0.5 para detectar más
            logger.info(f"🔍 Detecting vehicles with confidence >= {confidence_threshold}")
            
            vehicle_detections = await model_service.detect_vehicles(
                frame,
                confidence_threshold=confidence_threshold
            )
            
            logger.info(f"🚗 Received {len(vehicle_detections)} vehicle detections from YOLO")
            
            if len(vehicle_detections) == 0:
                logger.warning("⚠️  No vehicles detected, returning empty frame")
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                return {
                    "frame": frame_base64,
                    "detections": [],
                    "infractions_registered": 0,
                    "fps": 30.0,
                    "frame_number": self.frame_count,
                    "timestamp": datetime.now().isoformat()
                }
            
            detections = []
            infractions_detected = []
            
            logger.info(f"🔄 Processing {len(vehicle_detections)} vehicle detections...")
            
            # Process each vehicle detection
            for idx, vehicle in enumerate(vehicle_detections):
                try:
                    vehicle_id = f"v{idx}"
                    
                    logger.info(f"🚙 Processing vehicle #{idx+1}: {vehicle.get('vehicle_type', 'unknown')}")
                    
                    # Track vehicle
                    self.tracker.update(vehicle_id, vehicle)
                
                    # Try to detect license plate if OCR is enabled
                    license_plate = None
                    license_confidence = 0.0
                    
                    if config.get('enable_ocr', False):  # OCR desactivado por defecto
                        logger.info(f"🔤 Attempting OCR for vehicle #{idx+1}...")
                        plate_result = await model_service.detect_license_plate(
                            frame,
                            vehicle['bbox']
                        )
                        if plate_result:
                            license_plate, license_confidence = plate_result
                            vehicle['license_plate'] = license_plate
                            vehicle['license_confidence'] = license_confidence
                            logger.info(f"📋 Plate detected: {license_plate} (conf: {license_confidence:.2f})")
                    
                    # Check for infractions
                    infraction_type = None
                    infraction_data = {}
                    
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
                                    'speed_limit': speed_limit
                                }
                                vehicle['speed'] = round(simulated_speed, 1)
                                vehicle['has_infraction'] = True
                                logger.info(
                                    f"🚨 INFRACCIÓN DETECTADA: Vehículo a {simulated_speed:.1f} km/h "
                                    f"(límite: {speed_limit} km/h)"
                                )
                            else:
                                logger.info(f"✅ Vehicle within speed limit: {simulated_speed:.1f} km/h")
                        else:
                            logger.info(f"⏭️  Vehicle #{idx+1} skipped (no infraction this frame)")
                    else:
                        logger.info(f"⚠️  Simulation disabled or speeding not in config")
                    
                    # Speed violation detection (modo real)
                    if not simulate_infractions and 'speeding' in config.get('infractions', []) and config.get('enable_speed', True):
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
                                        'speed_limit': speed_limit
                                    }
                                    vehicle['has_infraction'] = True
                    
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
            
            # Clean old tracks periodically
            if self.frame_count % 100 == 0:
                self.tracker.clear_old_tracks()
                # Also clear old processed infractions (keep last 1000)
                if len(self.processed_infractions) > 1000:
                    self.processed_infractions = set(list(self.processed_infractions)[-500:])
            
            # Send infractions to Django backend (non-blocking)
            if infractions_detected:
                logger.info(f"💾 Sending {len(infractions_detected)} infractions to database...")
                asyncio.create_task(
                    self._save_infractions_to_database(infractions_detected)
                )
            else:
                logger.info(f"ℹ️  No infractions to save this frame")
            
            # Encode frame to base64 to send back to client
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            logger.info(f"📤 Sending result with {len(detections)} detections to client")
            
            return {
                "type": "detection",  # ✅ ADD THIS - frontend expects this field
                "frame": frame_base64,
                "detections": detections,
                "infractions_registered": len(infractions_detected),
                "fps": 30.0,
                "frame_number": self.frame_count,
                "timestamp": datetime.now().isoformat()
            }
            
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
            # Preparar detecciones para el formato de Django API
            formatted_detections = []
            
            for detection in detections_with_infractions:
                # Formato correcto para Django InfractionCreateSerializer
                formatted_detection = {
                    'infraction_type': detection.get('infraction_type', 'speed'),  # speed, red_light, etc
                    'detected_at': datetime.now().isoformat(),  # Campo requerido
                    'severity': 'medium',  # low, medium, high, critical
                    'status': 'pending',  # pending, validated, rejected, etc
                }
                
                # Agregar placa si existe
                if detection.get('license_plate'):
                    formatted_detection['license_plate_detected'] = detection['license_plate']
                    formatted_detection['license_plate_confidence'] = detection.get('license_confidence', 0.0)
                else:
                    # Si NO hay placa, dejar vacío
                    formatted_detection['license_plate_detected'] = ''
                    formatted_detection['license_plate_confidence'] = 0.0
                
                # Agregar velocidad si existe (para infracciones de velocidad)
                if detection.get('speed'):
                    formatted_detection['detected_speed'] = float(detection['speed'])
                
                # Agregar límite de velocidad si existe
                if detection.get('infraction_data'):
                    if 'speed_limit' in detection['infraction_data']:
                        formatted_detection['speed_limit'] = int(detection['infraction_data']['speed_limit'])
                    if 'detected_speed' in detection['infraction_data']:
                        formatted_detection['detected_speed'] = float(detection['infraction_data']['detected_speed'])
                
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
            
            # Enviar a Django (una por una)
            created_count = 0
            created_infractions = []
            
            for detection in formatted_detections:
                result = await django_api.create_infraction(
                    infraction_data=detection
                )
                
                if result:
                    created_count += 1
                    created_infractions.append(result)
            
            if created_count > 0:
                logger.info(
                    f"✅ Guardadas {created_count} infracciones en la base de datos"
                )
                # Log de infracciones guardadas
                for infraction in created_infractions:
                    license_plate = infraction.get('license_plate_detected') or 'SIN PLACA'
                    logger.info(
                        f"  - {infraction.get('infraction_code')}: "
                        f"{infraction.get('infraction_type')} | "
                        f"Vehículo: {license_plate} | "
                        f"Velocidad: {infraction.get('detected_speed', 'N/A')} km/h"
                    )
            else:
                logger.warning("No se pudieron guardar las infracciones")
            
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
