"""
FastAPI para gestión de configuración
====================================

API REST para administrar la configuración del sistema de detección de 
infracciones, incluyendo endpoints para CRUD de configuraciones y 
validación en tiempo real.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
import logging
import asyncio
from datetime import datetime
import json
import yaml

from config_manager import (
    config_manager, 
    MLModelConfig, 
    CameraConfig, 
    DetectionConfig, 
    SystemConfig,
    ConfigFormat
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Traffic System Configuration API",
    description="API para gestionar la configuración del sistema de detección de infracciones",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seguridad
security = HTTPBearer()

# Modelos Pydantic para requests/responses

class MLConfigRequest(BaseModel):
    """Request para configuración de modelo ML"""
    model_config = {"protected_namespaces": ()}
    
    model_name: str = Field(..., description="Nombre del modelo")
    model_path: str = Field(..., description="Ruta al archivo del modelo")
    model_version: str = Field(..., description="Versión del modelo")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Umbral de confianza")
    nms_threshold: float = Field(0.4, ge=0.0, le=1.0, description="Umbral NMS")
    input_size: tuple = Field((640, 640), description="Tamaño de entrada")
    device: str = Field("auto", description="Dispositivo de cómputo")
    batch_size: int = Field(1, gt=0, description="Tamaño de batch")
    half_precision: bool = Field(False, description="Usar precisión media")
    classes: Optional[List[int]] = Field(None, description="Clases a detectar")
    agnostic_nms: bool = Field(False, description="NMS agnóstico de clase")
    max_det: int = Field(1000, gt=0, description="Máximo de detecciones")

class CameraConfigRequest(BaseModel):
    """Request para configuración de cámara"""
    camera_id: str = Field(..., description="ID único de la cámara")
    name: str = Field(..., description="Nombre descriptivo")
    rtsp_url: str = Field(..., description="URL RTSP de la cámara")
    location: Dict[str, float] = Field(..., description="Ubicación (lat, lon)")
    active: bool = Field(True, description="Estado activo")
    fps: int = Field(30, gt=0, description="Frames por segundo")
    resolution: tuple = Field((1920, 1080), description="Resolución de video")
    codec: str = Field("h264", description="Codec de video")
    detection_zones: Optional[List[Dict]] = Field(None, description="Zonas de detección")
    speed_limit: int = Field(60, gt=0, description="Límite de velocidad en km/h")
    calibration_matrix: Optional[List[List[float]]] = Field(None, description="Matriz de calibración")
    distortion_coeffs: Optional[List[float]] = Field(None, description="Coeficientes de distorsión")
    recording_enabled: bool = Field(True, description="Grabación habilitada")
    snapshot_interval: int = Field(5, gt=0, description="Intervalo de snapshots en segundos")
    retention_days: int = Field(30, gt=0, description="Días de retención")
    
    @validator('rtsp_url')
    def validate_rtsp_url(cls, v):
        if not v.startswith('rtsp://'):
            raise ValueError('RTSP URL must start with rtsp://')
        return v
    
    @validator('location')
    def validate_location(cls, v):
        if 'lat' not in v or 'lon' not in v:
            raise ValueError('Location must contain lat and lon keys')
        if not -90 <= v['lat'] <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        if not -180 <= v['lon'] <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v

class DetectionConfigRequest(BaseModel):
    """Request para configuración de detección"""
    speed_threshold_warning: int = Field(5, gt=0, description="Umbral de advertencia de velocidad")
    speed_threshold_violation: int = Field(10, gt=0, description="Umbral de infracción de velocidad")
    max_disappeared: int = Field(30, gt=0, description="Máximo frames desaparecido")
    max_distance: float = Field(100.0, gt=0, description="Máxima distancia de tracking")
    ocr_confidence_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Umbral de confianza OCR")
    plate_formats: Optional[List[str]] = Field(None, description="Formatos de placa válidos")
    min_vehicle_area: int = Field(1000, gt=0, description="Área mínima de vehículo")
    max_vehicle_area: int = Field(500000, gt=0, description="Área máxima de vehículo")
    min_track_length: int = Field(10, gt=0, description="Longitud mínima de track")
    trajectory_smoothing: bool = Field(True, description="Suavizado de trayectoria")
    speed_smoothing_window: int = Field(5, gt=0, description="Ventana de suavizado de velocidad")
    
    @validator('speed_threshold_violation')
    def validate_speed_thresholds(cls, v, values):
        if 'speed_threshold_warning' in values and v <= values['speed_threshold_warning']:
            raise ValueError('Violation threshold must be greater than warning threshold')
        return v

class SystemConfigRequest(BaseModel):
    """Request para configuración del sistema"""
    system_name: str = Field("Traffic Violation Detection System", description="Nombre del sistema")
    version: str = Field("1.0.0", description="Versión del sistema")
    environment: str = Field("production", description="Entorno de ejecución")
    database_url: str = Field(..., description="URL de la base de datos")
    database_pool_size: int = Field(10, gt=0, description="Tamaño del pool de conexiones")
    database_max_overflow: int = Field(20, gt=0, description="Overflow máximo del pool")
    redis_url: str = Field(..., description="URL de Redis")
    cache_ttl_default: int = Field(3600, gt=0, description="TTL por defecto del cache")
    cache_max_memory: str = Field("512mb", description="Memoria máxima del cache")
    storage_backend: str = Field("minio", description="Backend de almacenamiento")
    storage_endpoint: str = Field("localhost:9000", description="Endpoint de almacenamiento")
    storage_bucket: str = Field("traffic-data", description="Bucket de almacenamiento")
    log_level: str = Field("INFO", description="Nivel de logging")
    log_format: str = Field("json", description="Formato de logs")
    log_file: str = Field("/var/log/traffic-system.log", description="Archivo de logs")
    log_max_size: str = Field("100MB", description="Tamaño máximo de logs")
    log_backup_count: int = Field(5, gt=0, description="Cantidad de backups de logs")
    metrics_enabled: bool = Field(True, description="Métricas habilitadas")
    metrics_port: int = Field(8090, gt=0, description="Puerto de métricas")
    health_check_interval: int = Field(30, gt=0, description="Intervalo de health check")
    jwt_secret_key: str = Field(..., description="Clave secreta JWT")
    jwt_algorithm: str = Field("HS256", description="Algoritmo JWT")
    jwt_expiration_hours: int = Field(24, gt=0, description="Expiración JWT en horas")
    password_min_length: int = Field(8, gt=0, description="Longitud mínima de contraseña")
    alert_email_enabled: bool = Field(False, description="Alertas por email habilitadas")
    alert_email_smtp: str = Field("", description="Servidor SMTP para alertas")
    alert_email_from: str = Field("", description="Email remitente de alertas")
    alert_webhook_url: str = Field("", description="URL webhook para alertas")

class ConfigValidationResponse(BaseModel):
    """Response de validación de configuración"""
    valid: bool
    errors: Dict[str, List[str]]
    warnings: List[str] = []

class ConfigExportResponse(BaseModel):
    """Response de exportación de configuración"""
    format: str
    content: str
    timestamp: datetime

# Dependencias

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Validar token de autenticación"""
    # Modo desarrollo: permitir acceso sin autenticación
    import os
    if os.getenv('ENVIRONMENT', 'production') == 'development':
        return {"user": "admin"}  # Skip auth in development
    
    # Producción: validar token
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Token required")
    return {"user": "admin"}  # TODO: Implementar validación real de JWT

# Eventos de inicio/cierre

@app.on_event("startup")
async def startup_event():
    """Inicializar configuraciones al inicio"""
    try:
        await config_manager.load_configurations()
        logger.info("Configuration Manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Configuration Manager: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar"""
    logger.info("Configuration API shutting down")

# Endpoints de configuración del sistema

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "Traffic System Configuration API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de verificación de salud"""
    try:
        # Verificar que el config manager esté funcionando
        system_config = config_manager.system_config
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "config_loaded": bool(system_config),
            "cameras_count": len(config_manager.camera_configs),
            "ml_models_count": len(config_manager.ml_configs)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# Endpoints de configuración del sistema

@app.get("/config/system", response_model=SystemConfig, tags=["System Config"])
async def get_system_config(user: dict = Depends(get_current_user)):
    """Obtener configuración del sistema"""
    return config_manager.system_config

@app.put("/config/system", tags=["System Config"])
async def update_system_config(
    config_request: SystemConfigRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Actualizar configuración del sistema"""
    try:
        # Crear nueva configuración
        new_config = SystemConfig(**config_request.dict())
        config_manager.system_config = new_config
        
        # Guardar en background
        background_tasks.add_task(config_manager.save_system_config)
        
        return {"message": "System configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints de configuración de modelos ML

@app.get("/config/ml", response_model=Dict[str, MLModelConfig], tags=["ML Config"])
async def get_ml_configs(user: dict = Depends(get_current_user)):
    """Obtener todas las configuraciones de modelos ML"""
    return config_manager.ml_configs

@app.get("/config/ml/{model_name}", response_model=MLModelConfig, tags=["ML Config"])
async def get_ml_config(model_name: str, user: dict = Depends(get_current_user)):
    """Obtener configuración de un modelo ML específico"""
    config = config_manager.get_ml_config(model_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"ML model config not found: {model_name}")
    return config

@app.post("/config/ml/{model_name}", tags=["ML Config"])
async def create_ml_config(
    model_name: str,
    config_request: MLConfigRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Crear configuración de modelo ML"""
    try:
        config_data = config_request.dict()
        config_data["model_name"] = model_name
        
        new_config = MLModelConfig(**config_data)
        config_manager.ml_configs[model_name] = new_config
        
        # Guardar en background
        background_tasks.add_task(config_manager.save_ml_config, model_name, new_config)
        
        return {"message": f"ML config created for {model_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/config/ml/{model_name}", tags=["ML Config"])
async def update_ml_config(
    model_name: str,
    config_request: MLConfigRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Actualizar configuración de modelo ML"""
    if model_name not in config_manager.ml_configs:
        raise HTTPException(status_code=404, detail=f"ML model config not found: {model_name}")
    
    try:
        config_data = config_request.dict()
        config_data["model_name"] = model_name
        
        updated_config = MLModelConfig(**config_data)
        config_manager.ml_configs[model_name] = updated_config
        
        # Guardar en background
        background_tasks.add_task(config_manager.save_ml_config, model_name, updated_config)
        
        return {"message": f"ML config updated for {model_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/config/ml/{model_name}", tags=["ML Config"])
async def delete_ml_config(
    model_name: str,
    user: dict = Depends(get_current_user)
):
    """Eliminar configuración de modelo ML"""
    if model_name not in config_manager.ml_configs:
        raise HTTPException(status_code=404, detail=f"ML model config not found: {model_name}")
    
    del config_manager.ml_configs[model_name]
    
    # TODO: Eliminar archivo de configuración
    
    return {"message": f"ML config deleted for {model_name}"}

# Endpoints de configuración de cámaras

@app.get("/config/cameras", response_model=Dict[str, CameraConfig], tags=["Camera Config"])
async def get_camera_configs(
    active_only: bool = False,
    user: dict = Depends(get_current_user)
):
    """Obtener configuraciones de cámaras"""
    if active_only:
        return config_manager.get_active_cameras()
    return config_manager.get_all_cameras()

@app.get("/config/cameras/{camera_id}", response_model=CameraConfig, tags=["Camera Config"])
async def get_camera_config(camera_id: str, user: dict = Depends(get_current_user)):
    """Obtener configuración de una cámara específica"""
    config = config_manager.get_camera_config(camera_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Camera config not found: {camera_id}")
    return config

@app.post("/config/cameras/{camera_id}", tags=["Camera Config"])
async def create_camera_config(
    camera_id: str,
    config_request: CameraConfigRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Crear configuración de cámara"""
    try:
        config_data = config_request.dict()
        config_data["camera_id"] = camera_id
        
        new_config = CameraConfig(**config_data)
        config_manager.camera_configs[camera_id] = new_config
        
        # Guardar en background
        background_tasks.add_task(config_manager.save_camera_config, camera_id, new_config)
        
        return {"message": f"Camera config created for {camera_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/config/cameras/{camera_id}", tags=["Camera Config"])
async def update_camera_config(
    camera_id: str,
    config_request: CameraConfigRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Actualizar configuración de cámara"""
    if camera_id not in config_manager.camera_configs:
        raise HTTPException(status_code=404, detail=f"Camera config not found: {camera_id}")
    
    try:
        config_data = config_request.dict()
        config_data["camera_id"] = camera_id
        
        updated_config = CameraConfig(**config_data)
        config_manager.camera_configs[camera_id] = updated_config
        
        # Guardar en background
        background_tasks.add_task(config_manager.save_camera_config, camera_id, updated_config)
        
        return {"message": f"Camera config updated for {camera_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/config/cameras/{camera_id}", tags=["Camera Config"])
async def delete_camera_config(
    camera_id: str,
    user: dict = Depends(get_current_user)
):
    """Eliminar configuración de cámara"""
    if camera_id not in config_manager.camera_configs:
        raise HTTPException(status_code=404, detail=f"Camera config not found: {camera_id}")
    
    del config_manager.camera_configs[camera_id]
    
    # TODO: Eliminar archivo de configuración
    
    return {"message": f"Camera config deleted for {camera_id}"}

@app.patch("/config/cameras/{camera_id}/status", tags=["Camera Config"])
async def update_camera_status(
    camera_id: str,
    active: bool,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Actualizar estado de una cámara"""
    if camera_id not in config_manager.camera_configs:
        raise HTTPException(status_code=404, detail=f"Camera config not found: {camera_id}")
    
    # Actualizar en background
    background_tasks.add_task(config_manager.update_camera_status, camera_id, active)
    
    return {"message": f"Camera {camera_id} status updated to {'active' if active else 'inactive'}"}

# Endpoints de configuración de detección

@app.get("/config/detection", response_model=DetectionConfig, tags=["Detection Config"])
async def get_detection_config(user: dict = Depends(get_current_user)):
    """Obtener configuración de detección"""
    return config_manager.detection_config

@app.put("/config/detection", tags=["Detection Config"])
async def update_detection_config(
    config_request: DetectionConfigRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Actualizar configuración de detección"""
    try:
        new_config = DetectionConfig(**config_request.dict())
        config_manager.detection_config = new_config
        
        # Guardar en background
        background_tasks.add_task(config_manager.save_detection_config)
        
        return {"message": "Detection configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/config/detection/threshold/{threshold_type}", tags=["Detection Config"])
async def update_detection_threshold(
    threshold_type: str,
    value: float,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Actualizar un umbral específico de detección"""
    valid_thresholds = [
        "speed_threshold_warning",
        "speed_threshold_violation", 
        "ocr_confidence_threshold"
    ]
    
    if threshold_type not in valid_thresholds:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid threshold type. Valid types: {valid_thresholds}"
        )
    
    # Actualizar en background
    background_tasks.add_task(config_manager.update_detection_threshold, threshold_type, value)
    
    return {"message": f"Threshold {threshold_type} updated to {value}"}

# Endpoints de validación y utilidades

@app.post("/config/validate", response_model=ConfigValidationResponse, tags=["Validation"])
async def validate_configuration(user: dict = Depends(get_current_user)):
    """Validar todas las configuraciones"""
    errors = await config_manager.validate_configurations()
    
    # Generar warnings adicionales
    warnings = []
    if config_manager.system_config.environment == "production":
        if config_manager.system_config.jwt_secret_key == "change-me-in-production":
            warnings.append("JWT secret key should be changed in production environment")
    
    return ConfigValidationResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

@app.get("/config/export", response_model=ConfigExportResponse, tags=["Import/Export"])
async def export_configuration(
    format: str = "yaml",
    user: dict = Depends(get_current_user)
):
    """Exportar toda la configuración"""
    try:
        config_format = ConfigFormat(format.lower())
        content = config_manager.export_configuration(config_format)
        
        return ConfigExportResponse(
            format=format,
            content=content,
            timestamp=datetime.now()
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Supported formats: {[f.value for f in ConfigFormat]}"
        )

@app.post("/config/import", tags=["Import/Export"])
async def import_configuration(
    content: str,
    background_tasks: BackgroundTasks,
    format: str = "yaml",
    user: dict = Depends(get_current_user)
):
    """Importar configuración desde string"""
    try:
        config_format = ConfigFormat(format.lower())
        
        # Importar en background
        background_tasks.add_task(config_manager.import_configuration, content, config_format)
        
        return {"message": "Configuration import started"}
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Supported formats: {[f.value for f in ConfigFormat]}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/config/backup", tags=["Backup"])
async def backup_configuration(user: dict = Depends(get_current_user)):
    """Crear backup de la configuración actual"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_content = config_manager.export_configuration(ConfigFormat.YAML)
        
        # En un entorno real, guardaría el backup en un sistema de almacenamiento
        return {
            "message": "Backup created successfully",
            "timestamp": timestamp,
            "size": len(backup_content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de información del sistema

@app.get("/info/stats", tags=["System Info"])
async def get_system_stats(user: dict = Depends(get_current_user)):
    """Obtener estadísticas del sistema de configuración"""
    return {
        "cameras": {
            "total": len(config_manager.camera_configs),
            "active": len(config_manager.get_active_cameras()),
            "inactive": len(config_manager.camera_configs) - len(config_manager.get_active_cameras())
        },
        "ml_models": {
            "total": len(config_manager.ml_configs),
            "models": list(config_manager.ml_configs.keys())
        },
        "system": {
            "environment": config_manager.system_config.environment,
            "version": config_manager.system_config.version,
            "name": config_manager.system_config.system_name
        }
    }

@app.get("/info/cameras/locations", tags=["System Info"])
async def get_camera_locations(user: dict = Depends(get_current_user)):
    """Obtener ubicaciones de todas las cámaras para mapas"""
    locations = []
    for camera_id, config in config_manager.camera_configs.items():
        locations.append({
            "camera_id": camera_id,
            "name": config.name,
            "location": config.location,
            "active": config.active,
            "speed_limit": config.speed_limit
        })
    return locations

# WebSocket para notificaciones en tiempo real

from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    """Gestor de conexiones WebSocket"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Remover conexiones cerradas
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws/config-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para notificaciones de cambios de configuración"""
    await manager.connect(websocket)
    try:
        while True:
            # Mantener conexión viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Observador para notificar cambios por WebSocket
async def config_change_observer(event_type: str, *args):
    """Observador para notificar cambios de configuración por WebSocket"""
    message = {
        "type": "config_change",
        "event": event_type,
        "data": args,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

# Registrar observador
config_manager.add_observer(config_change_observer)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)