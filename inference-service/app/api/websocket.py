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
                await self.initialize_models()
            
            # Decodificar la imagen base64
            image_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("Failed to decode frame")
                return {"error": "Invalid frame data"}
            
            height, width = frame.shape[:2]
            self.frame_count += 1
            
            # Detect vehicles using YOLOv8
            vehicle_detections = await model_service.detect_vehicles(
                frame,
                confidence_threshold=config.get('confidence_threshold', 0.7)
            )
            
            detections = []
            infractions_detected = []
            
            # Process each vehicle detection
            for idx, vehicle in enumerate(vehicle_detections):
                vehicle_id = f"v{idx}"
                
                # Track vehicle
                self.tracker.update(vehicle_id, vehicle)
                
                # Try to detect license plate if OCR is enabled
                license_plate = None
                license_confidence = 0.0
                
                if config.get('enable_ocr', True):
                    plate_result = await model_service.detect_license_plate(
                        frame,
                        vehicle['bbox']
                    )
                    if plate_result:
                        license_plate, license_confidence = plate_result
                        vehicle['license_plate'] = license_plate
                        vehicle['license_confidence'] = license_confidence
                
                # Check for infractions
                infraction_type = None
                infraction_data = {}
                
                # Speed violation detection
                if 'speeding' in config.get('infractions', []) and config.get('enable_speed', True):
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
                                infraction_type = 'speeding'
                                infraction_data = {
                                    'detected_speed': estimated_speed,
                                    'speed_limit': speed_limit
                                }
                
                # Red light violation (simplified - would need traffic light detection)
                if 'red_light' in config.get('infractions', []):
                    # TODO: Implement traffic light detection
                    # For MVP, randomly simulate based on position
                    pass
                
                # Lane invasion (simplified - would need lane detection)
                if 'lane_invasion' in config.get('infractions', []):
                    # TODO: Implement lane detection
                    # For MVP, check if vehicle is at edge of frame
                    pass
                
                # Create detection object
                detection = {
                    'id': f"{self.frame_count}-{idx}",
                    'type': 'infraction' if infraction_type else 'vehicle',
                    'vehicle_type': vehicle.get('vehicle_type', 'car'),
                    'confidence': vehicle['confidence'],
                    'bbox': vehicle['bbox'],
                    'timestamp': datetime.now().isoformat()
                }
                
                if license_plate:
                    detection['license_plate'] = license_plate
                    detection['license_confidence'] = license_confidence
                
                if vehicle.get('speed'):
                    detection['speed'] = vehicle['speed']
                
                if infraction_type:
                    detection['infraction_type'] = infraction_type
                    
                    # Register infraction in database
                    infraction_key = f"{license_plate}-{infraction_type}-{self.frame_count // 30}"
                    if license_plate and infraction_key not in self.processed_infractions:
                        await self._register_infraction(
                            license_plate=license_plate,
                            vehicle_type=vehicle.get('vehicle_type', 'car'),
                            infraction_type=infraction_type,
                            infraction_data=infraction_data,
                            confidence=vehicle['confidence'],
                            frame=frame,
                            bbox=vehicle['bbox']
                        )
                        self.processed_infractions.add(infraction_key)
                        infractions_detected.append(detection)
                
                detections.append(detection)
            
            # Clean old tracks periodically
            if self.frame_count % 100 == 0:
                self.tracker.clear_old_tracks()
                # Also clear old processed infractions (keep last 1000)
                if len(self.processed_infractions) > 1000:
                    self.processed_infractions = set(list(self.processed_infractions)[-500:])
            
            return {
                "detections": detections,
                "infractions_registered": len(infractions_detected),
                "fps": 30.0,
                "frame_count": self.frame_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    async def _register_infraction(
        self,
        license_plate: str,
        vehicle_type: str,
        infraction_type: str,
        infraction_data: Dict,
        confidence: float,
        frame: np.ndarray,
        bbox: Dict
    ):
        """
        Register infraction in Django database
        """
        try:
            logger.info(f"Registering infraction: {infraction_type} for {license_plate}")
            
            # Map infraction type to Django model format
            infraction_type_map = {
                'speeding': 'speed',
                'red_light': 'red_light',
                'lane_invasion': 'wrong_lane'
            }
            
            django_infraction_type = infraction_type_map.get(infraction_type, 'other')
            
            # Get or create vehicle
            vehicle = await django_api.get_or_create_vehicle(
                license_plate=license_plate,
                vehicle_type=vehicle_type
            )
            
            if not vehicle:
                logger.warning(f"Could not get/create vehicle for {license_plate}")
                return
            
            # Prepare infraction data for Django
            # For MVP, using default device and zone - in production, these would be provided
            infraction_payload = {
                'infraction_type': django_infraction_type,
                'severity': 'medium' if infraction_type == 'speeding' else 'high',
                'vehicle': vehicle['id'],
                'license_plate_detected': license_plate,
                'license_plate_confidence': confidence,
                'detected_at': datetime.now().isoformat(),
                'status': 'pending',
                'evidence_metadata': {
                    'detection_confidence': confidence,
                    'bbox': bbox,
                    'infraction_data': infraction_data
                }
            }
            
            # Add speed-specific data
            if infraction_type == 'speeding':
                infraction_payload['detected_speed'] = infraction_data.get('detected_speed')
                infraction_payload['speed_limit'] = infraction_data.get('speed_limit')
            
            # Create infraction in Django
            result = await django_api.create_infraction(infraction_payload)
            
            if result:
                logger.info(f"Infraction registered successfully: {result.get('id')}")
            else:
                logger.error(f"Failed to register infraction for {license_plate}")
                
        except Exception as e:
            logger.error(f"Error registering infraction: {str(e)}", exc_info=True)


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
