import os
import json
from typing import Optional, List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Application
    APP_NAME: str = "Traffic Inference Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    WORKERS: int = 1
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://admin:admin123@postgres:5432/traffic_system"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://admin:admin123@rabbitmq:5672/"
    
    # MinIO/S3
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "admin123"
    MINIO_BUCKET: str = "traffic-evidence"
    MINIO_SECURE: bool = False
    
    # Video Processing
    MAX_CONCURRENT_STREAMS: int = 10
    FRAME_BUFFER_SIZE: int = 30
    RTSP_TIMEOUT: int = 30
    
    # EZVIZ Camera Configuration
    EZVIZ_RTSP_URL: str = "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream"
    EZVIZ_RTSP_URL_SUB: str = "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/sub/av_stream"
    EZVIZ_IP: str = "192.168.1.100"
    EZVIZ_USERNAME: str = "admin"
    EZVIZ_PASSWORD: str = "Abc123456"
    EZVIZ_RTSP_PORT: int = 554
    EZVIZ_HTTP_PORT: int = 80
    
    # Logging
    LOG_LEVEL: str = "DEBUG"  # Cambiado temporalmente para diagnosticar red light detection
    
    # ML Models
    YOLO_MODEL_PATH: str = "/app/models/yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5
    YOLO_IOU_THRESHOLD: float = 0.45
    OCR_LANGUAGES: List[str] = ['en']  # English for alphanumeric plates
    OCR_GPU: bool = False
    
    @field_validator('OCR_LANGUAGES', mode='before')
    @classmethod
    def validate_ocr_languages(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat as single language
                return [v]
        return v
    
    # Django Backend API
    DJANGO_API_URL: str = os.getenv("DJANGO_API_URL", "http://localhost:8000")
    DJANGO_API_TIMEOUT: int = 30
    LOG_FORMAT: str = "json"  # json or console
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()