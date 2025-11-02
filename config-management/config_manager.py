"""
Sistema de Configuración Avanzada
=================================

Sistema centralizado para gestionar toda la configuración del sistema de 
detección de infracciones, incluyendo parámetros ML, configuración de cámaras,
umbrales de detección y settings operacionales.
"""

import json
import logging
import os
import yaml
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigSource(Enum):
    """Fuentes de configuración disponibles"""
    FILE = "file"
    DATABASE = "database"
    ENVIRONMENT = "environment"
    REMOTE = "remote"

class ConfigFormat(Enum):
    """Formatos de configuración soportados"""
    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    TOML = "toml"

@dataclass
class MLModelConfig:
    """Configuración de modelos ML"""
    model_name: str
    model_path: str
    model_version: str
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    input_size: tuple = (640, 640)
    device: str = "auto"  # auto, cpu, cuda:0, etc.
    batch_size: int = 1
    half_precision: bool = False
    
    # Configuración específica de YOLO
    classes: List[int] = None
    agnostic_nms: bool = False
    max_det: int = 1000
    
    # Configuración de optimización
    tensorrt: bool = False
    onnx: bool = False
    openvino: bool = False

@dataclass
class CameraConfig:
    """Configuración de cámara individual"""
    camera_id: str
    name: str
    rtsp_url: str
    location: Dict[str, float]  # lat, lon
    active: bool = True
    
    # Configuración de video
    fps: int = 30
    resolution: tuple = (1920, 1080)
    codec: str = "h264"
    
    # Configuración de detección
    detection_zones: List[Dict] = None  # Polígonos de detección
    speed_limit: int = 60  # km/h
    
    # Configuración de calibración
    calibration_matrix: List[List[float]] = None
    distortion_coeffs: List[float] = None
    
    # Configuración operacional
    recording_enabled: bool = True
    snapshot_interval: int = 5  # segundos
    retention_days: int = 30

@dataclass
class DetectionConfig:
    """Configuración de parámetros de detección"""
    # Umbrales de velocidad
    speed_threshold_warning: int = 5  # km/h sobre límite para warning
    speed_threshold_violation: int = 10  # km/h sobre límite para infracción
    
    # Configuración de tracking
    max_disappeared: int = 30  # frames
    max_distance: float = 100  # pixels
    
    # Configuración de OCR
    ocr_confidence_threshold: float = 0.8
    plate_formats: List[str] = None  # ["ABC-123", "ABC-1234"]
    
    # Filtros de detección
    min_vehicle_area: int = 1000  # pixels²
    max_vehicle_area: int = 500000  # pixels²
    min_track_length: int = 10  # frames
    
    # Configuración de análisis
    trajectory_smoothing: bool = True
    speed_smoothing_window: int = 5  # frames

@dataclass
class SystemConfig:
    """Configuración general del sistema"""
    # Información del sistema
    system_name: str = "Traffic Violation Detection System"
    version: str = "1.0.0"
    environment: str = "production"  # development, staging, production
    
    # Configuración de base de datos
    database_url: str = "postgresql://user:pass@localhost:5432/traffic_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Configuración de cache
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_default: int = 3600  # segundos
    cache_max_memory: str = "512mb"
    
    # Configuración de storage
    storage_backend: str = "minio"  # minio, s3, local
    storage_endpoint: str = "localhost:9000"
    storage_bucket: str = "traffic-data"
    
    # Configuración de logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "/var/log/traffic-system.log"
    log_max_size: str = "100MB"
    log_backup_count: int = 5
    
    # Configuración de monitoring
    metrics_enabled: bool = True
    metrics_port: int = 8090
    health_check_interval: int = 30  # segundos
    
    # Configuración de seguridad
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    
    # Configuración de alertas
    alert_email_enabled: bool = False
    alert_email_smtp: str = "smtp.gmail.com:587"
    alert_email_from: str = "alerts@traffic-system.com"
    alert_webhook_url: str = ""

class ConfigManager:
    """Gestor centralizado de configuración"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuraciones cargadas
        self.ml_configs: Dict[str, MLModelConfig] = {}
        self.camera_configs: Dict[str, CameraConfig] = {}
        self.detection_config: DetectionConfig = DetectionConfig()
        self.system_config: SystemConfig = SystemConfig()
        
        # Observadores para cambios de configuración
        self.observers: List[callable] = []
        
        # Cache de configuración
        self._config_cache: Dict[str, Any] = {}
        self._last_loaded: Dict[str, datetime] = {}
    
    async def load_configurations(self):
        """Cargar todas las configuraciones desde archivos"""
        try:
            # Cargar configuración del sistema
            await self._load_system_config()
            
            # Cargar configuraciones de modelos ML
            await self._load_ml_configs()
            
            # Cargar configuraciones de cámaras
            await self._load_camera_configs()
            
            # Cargar configuración de detección
            await self._load_detection_config()
            
            logger.info("All configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
            raise
    
    async def _load_system_config(self):
        """Cargar configuración del sistema"""
        config_file = self.config_dir / "system.yaml"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
                self.system_config = SystemConfig(**data)
        else:
            # Crear configuración por defecto
            await self.save_system_config()
        
        # Sobrescribir con variables de entorno
        self._override_from_env(self.system_config)
    
    async def _load_ml_configs(self):
        """Cargar configuraciones de modelos ML"""
        ml_config_dir = self.config_dir / "models"
        ml_config_dir.mkdir(exist_ok=True)
        
        for config_file in ml_config_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f)
                    config = MLModelConfig(**data)
                    self.ml_configs[config.model_name] = config
            except Exception as e:
                logger.error(f"Error loading ML config {config_file}: {e}")
        
        # Crear configuraciones por defecto si no existen
        if not self.ml_configs:
            await self._create_default_ml_configs()
    
    async def _load_camera_configs(self):
        """Cargar configuraciones de cámaras"""
        camera_config_dir = self.config_dir / "cameras"
        camera_config_dir.mkdir(exist_ok=True)
        
        for config_file in camera_config_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f)
                    config = CameraConfig(**data)
                    self.camera_configs[config.camera_id] = config
            except Exception as e:
                logger.error(f"Error loading camera config {config_file}: {e}")
        
        # Crear configuración por defecto si no existe
        if not self.camera_configs:
            await self._create_default_camera_configs()
    
    async def _load_detection_config(self):
        """Cargar configuración de detección"""
        config_file = self.config_dir / "detection.yaml"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
                self.detection_config = DetectionConfig(**data)
        else:
            await self.save_detection_config()
    
    async def _create_default_ml_configs(self):
        """Crear configuraciones ML por defecto"""
        # YOLOv8 para detección de vehículos
        yolo_config = MLModelConfig(
            model_name="yolov8n_vehicles",
            model_path="models/yolov8n.pt",
            model_version="8.0.0",
            confidence_threshold=0.5,
            nms_threshold=0.4,
            input_size=(640, 640),
            classes=[2, 3, 5, 7],  # car, motorcycle, bus, truck
            device="auto"
        )
        
        # EasyOCR para reconocimiento de placas
        ocr_config = MLModelConfig(
            model_name="easyocr_plates",
            model_path="models/easyocr",
            model_version="1.7.0",
            confidence_threshold=0.8,
            device="auto"
        )
        
        self.ml_configs["yolov8n_vehicles"] = yolo_config
        self.ml_configs["easyocr_plates"] = ocr_config
        
        await self.save_ml_config("yolov8n_vehicles", yolo_config)
        await self.save_ml_config("easyocr_plates", ocr_config)
    
    async def _create_default_camera_configs(self):
        """Crear configuraciones de cámara por defecto"""
        # Cámara de ejemplo
        camera_config = CameraConfig(
            camera_id="CAM001",
            name="Av. Javier Prado - San Isidro",
            rtsp_url="rtsp://admin:password@192.168.1.100:554/stream1",
            location={"lat": -12.0864, "lon": -77.0365},
            speed_limit=60,
            detection_zones=[
                {
                    "name": "lane1",
                    "polygon": [[100, 200], [500, 200], [500, 400], [100, 400]]
                }
            ]
        )
        
        self.camera_configs["CAM001"] = camera_config
        await self.save_camera_config("CAM001", camera_config)
    
    def _override_from_env(self, config: SystemConfig):
        """Sobrescribir configuración con variables de entorno"""
        env_mappings = {
            "DATABASE_URL": "database_url",
            "REDIS_URL": "redis_url",
            "JWT_SECRET_KEY": "jwt_secret_key",
            "LOG_LEVEL": "log_level",
            "ENVIRONMENT": "environment"
        }
        
        for env_var, attr_name in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                setattr(config, attr_name, env_value)
    
    async def save_system_config(self):
        """Guardar configuración del sistema"""
        config_file = self.config_dir / "system.yaml"
        data = asdict(self.system_config)
        
        with open(config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        logger.info("System configuration saved")
    
    async def save_ml_config(self, model_name: str, config: MLModelConfig):
        """Guardar configuración de modelo ML"""
        ml_config_dir = self.config_dir / "models"
        ml_config_dir.mkdir(exist_ok=True)
        
        config_file = ml_config_dir / f"{model_name}.yaml"
        data = asdict(config)
        
        with open(config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        logger.info(f"ML config saved for {model_name}")
    
    async def save_camera_config(self, camera_id: str, config: CameraConfig):
        """Guardar configuración de cámara"""
        camera_config_dir = self.config_dir / "cameras"
        camera_config_dir.mkdir(exist_ok=True)
        
        config_file = camera_config_dir / f"{camera_id}.yaml"
        data = asdict(config)
        
        with open(config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        logger.info(f"Camera config saved for {camera_id}")
    
    async def save_detection_config(self):
        """Guardar configuración de detección"""
        config_file = self.config_dir / "detection.yaml"
        data = asdict(self.detection_config)
        
        with open(config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        logger.info("Detection configuration saved")
    
    def get_ml_config(self, model_name: str) -> Optional[MLModelConfig]:
        """Obtener configuración de modelo ML"""
        return self.ml_configs.get(model_name)
    
    def get_camera_config(self, camera_id: str) -> Optional[CameraConfig]:
        """Obtener configuración de cámara"""
        return self.camera_configs.get(camera_id)
    
    def get_all_cameras(self) -> Dict[str, CameraConfig]:
        """Obtener todas las configuraciones de cámaras"""
        return self.camera_configs.copy()
    
    def get_active_cameras(self) -> Dict[str, CameraConfig]:
        """Obtener solo cámaras activas"""
        return {
            cam_id: config 
            for cam_id, config in self.camera_configs.items() 
            if config.active
        }
    
    async def update_camera_status(self, camera_id: str, active: bool):
        """Actualizar estado de una cámara"""
        if camera_id in self.camera_configs:
            self.camera_configs[camera_id].active = active
            await self.save_camera_config(camera_id, self.camera_configs[camera_id])
            await self._notify_observers("camera_status_changed", camera_id, active)
    
    async def update_detection_threshold(self, threshold_type: str, value: float):
        """Actualizar umbral de detección"""
        if hasattr(self.detection_config, threshold_type):
            setattr(self.detection_config, threshold_type, value)
            await self.save_detection_config()
            await self._notify_observers("detection_threshold_changed", threshold_type, value)
    
    def add_observer(self, callback: callable):
        """Agregar observador para cambios de configuración"""
        self.observers.append(callback)
    
    def remove_observer(self, callback: callable):
        """Remover observador"""
        if callback in self.observers:
            self.observers.remove(callback)
    
    async def _notify_observers(self, event_type: str, *args):
        """Notificar a observadores sobre cambios"""
        for observer in self.observers:
            try:
                if asyncio.iscoroutinefunction(observer):
                    await observer(event_type, *args)
                else:
                    observer(event_type, *args)
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")
    
    async def validate_configurations(self) -> Dict[str, List[str]]:
        """Validar todas las configuraciones"""
        errors = {
            "system": [],
            "ml_models": [],
            "cameras": [],
            "detection": []
        }
        
        # Validar configuración del sistema
        errors["system"].extend(await self._validate_system_config())
        
        # Validar configuraciones ML
        for model_name, config in self.ml_configs.items():
            model_errors = await self._validate_ml_config(config)
            if model_errors:
                errors["ml_models"].extend([f"{model_name}: {err}" for err in model_errors])
        
        # Validar configuraciones de cámaras
        for camera_id, config in self.camera_configs.items():
            camera_errors = await self._validate_camera_config(config)
            if camera_errors:
                errors["cameras"].extend([f"{camera_id}: {err}" for err in camera_errors])
        
        # Validar configuración de detección
        errors["detection"].extend(await self._validate_detection_config())
        
        return {k: v for k, v in errors.items() if v}
    
    async def _validate_system_config(self) -> List[str]:
        """Validar configuración del sistema"""
        errors = []
        
        # Validar URLs de conexión
        if not self.system_config.database_url:
            errors.append("Database URL is required")
        
        if not self.system_config.redis_url:
            errors.append("Redis URL is required")
        
        # Validar configuración de seguridad
        if self.system_config.jwt_secret_key == "change-me-in-production":
            errors.append("JWT secret key must be changed in production")
        
        if len(self.system_config.jwt_secret_key) < 32:
            errors.append("JWT secret key should be at least 32 characters")
        
        return errors
    
    async def _validate_ml_config(self, config: MLModelConfig) -> List[str]:
        """Validar configuración de modelo ML"""
        errors = []
        
        # Validar path del modelo
        if not Path(config.model_path).exists():
            errors.append(f"Model file not found: {config.model_path}")
        
        # Validar umbrales
        if not 0 <= config.confidence_threshold <= 1:
            errors.append("Confidence threshold must be between 0 and 1")
        
        if not 0 <= config.nms_threshold <= 1:
            errors.append("NMS threshold must be between 0 and 1")
        
        return errors
    
    async def _validate_camera_config(self, config: CameraConfig) -> List[str]:
        """Validar configuración de cámara"""
        errors = []
        
        # Validar URL RTSP
        if not config.rtsp_url.startswith("rtsp://"):
            errors.append("RTSP URL must start with rtsp://")
        
        # Validar coordenadas
        lat, lon = config.location.get("lat"), config.location.get("lon")
        if not (-90 <= lat <= 90):
            errors.append("Latitude must be between -90 and 90")
        
        if not (-180 <= lon <= 180):
            errors.append("Longitude must be between -180 and 180")
        
        # Validar límite de velocidad
        if config.speed_limit <= 0:
            errors.append("Speed limit must be positive")
        
        return errors
    
    async def _validate_detection_config(self) -> List[str]:
        """Validar configuración de detección"""
        errors = []
        
        # Validar umbrales de velocidad
        if self.detection_config.speed_threshold_warning <= 0:
            errors.append("Speed warning threshold must be positive")
        
        if self.detection_config.speed_threshold_violation <= self.detection_config.speed_threshold_warning:
            errors.append("Speed violation threshold must be greater than warning threshold")
        
        # Validar configuración de OCR
        if not 0 <= self.detection_config.ocr_confidence_threshold <= 1:
            errors.append("OCR confidence threshold must be between 0 and 1")
        
        return errors
    
    def export_configuration(self, format: ConfigFormat = ConfigFormat.YAML) -> str:
        """Exportar toda la configuración"""
        config_data = {
            "system": asdict(self.system_config),
            "detection": asdict(self.detection_config),
            "ml_models": {name: asdict(config) for name, config in self.ml_configs.items()},
            "cameras": {cam_id: asdict(config) for cam_id, config in self.camera_configs.items()}
        }
        
        if format == ConfigFormat.YAML:
            return yaml.dump(config_data, default_flow_style=False)
        elif format == ConfigFormat.JSON:
            return json.dumps(config_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def import_configuration(self, config_data: str, format: ConfigFormat = ConfigFormat.YAML):
        """Importar configuración desde string"""
        try:
            if format == ConfigFormat.YAML:
                data = yaml.safe_load(config_data)
            elif format == ConfigFormat.JSON:
                data = json.loads(config_data)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Importar configuraciones
            if "system" in data:
                self.system_config = SystemConfig(**data["system"])
                await self.save_system_config()
            
            if "detection" in data:
                self.detection_config = DetectionConfig(**data["detection"])
                await self.save_detection_config()
            
            if "ml_models" in data:
                for model_name, model_data in data["ml_models"].items():
                    config = MLModelConfig(**model_data)
                    self.ml_configs[model_name] = config
                    await self.save_ml_config(model_name, config)
            
            if "cameras" in data:
                for camera_id, camera_data in data["cameras"].items():
                    config = CameraConfig(**camera_data)
                    self.camera_configs[camera_id] = config
                    await self.save_camera_config(camera_id, config)
            
            logger.info("Configuration imported successfully")
            
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            raise

# Instancia global del gestor de configuración
config_manager = ConfigManager()

# Decorador para inyección de configuración
def inject_config(config_type: str):
    """Decorador para inyectar configuración en funciones"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            if config_type == "system":
                kwargs["config"] = config_manager.system_config
            elif config_type == "detection":
                kwargs["config"] = config_manager.detection_config
            elif config_type.startswith("ml:"):
                model_name = config_type.split(":", 1)[1]
                kwargs["config"] = config_manager.get_ml_config(model_name)
            elif config_type.startswith("camera:"):
                camera_id = config_type.split(":", 1)[1]
                kwargs["config"] = config_manager.get_camera_config(camera_id)
            
            return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            if config_type == "system":
                kwargs["config"] = config_manager.system_config
            elif config_type == "detection":
                kwargs["config"] = config_manager.detection_config
            elif config_type.startswith("ml:"):
                model_name = config_type.split(":", 1)[1]
                kwargs["config"] = config_manager.get_ml_config(model_name)
            elif config_type.startswith("camera:"):
                camera_id = config_type.split(":", 1)[1]
                kwargs["config"] = config_manager.get_camera_config(camera_id)
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

if __name__ == "__main__":
    # Ejemplo de uso
    
    async def main():
        # Inicializar gestor de configuración
        manager = ConfigManager("config")
        await manager.load_configurations()
        
        # Obtener configuración de cámara
        cam_config = manager.get_camera_config("CAM001")
        if cam_config:
            print(f"Camera: {cam_config.name}")
            print(f"Speed limit: {cam_config.speed_limit} km/h")
        
        # Obtener configuración ML
        ml_config = manager.get_ml_config("yolov8n_vehicles")
        if ml_config:
            print(f"Model: {ml_config.model_name}")
            print(f"Confidence: {ml_config.confidence_threshold}")
        
        # Validar configuraciones
        errors = await manager.validate_configurations()
        if errors:
            print("Configuration errors found:")
            for category, error_list in errors.items():
                for error in error_list:
                    print(f"  {category}: {error}")
        else:
            print("All configurations are valid!")
        
        # Exportar configuración
        config_yaml = manager.export_configuration(ConfigFormat.YAML)
        print("\nExported configuration:")
        print(config_yaml[:500] + "..." if len(config_yaml) > 500 else config_yaml)
    
    asyncio.run(main())