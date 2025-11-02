# API ML Service - Documentación Técnica

## Información General

### Base URL
- **Desarrollo**: `http://localhost:8001`
- **Staging**: `https://staging-ml.trafficsystem.com`
- **Producción**: `https://ml.trafficsystem.com`

### Framework
FastAPI con Pydantic para validación y documentación automática.

### Documentación Interactiva
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

## Endpoints de Salud

### GET /health
Verificar estado del servicio ML.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models": {
    "license_plate_detection": {
      "status": "loaded",
      "version": "v2.1",
      "accuracy": 0.98
    },
    "vehicle_classification": {
      "status": "loaded", 
      "version": "v1.5",
      "accuracy": 0.95
    },
    "infraction_detection": {
      "status": "loaded",
      "version": "v3.0", 
      "accuracy": 0.92
    }
  },
  "gpu_available": true,
  "memory_usage": "2.1GB/8GB",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### GET /metrics
Métricas de Prometheus para monitoreo.

## Detección de Placas

### POST /detect/license-plates
Detectar placas en imágenes o videos.

**Request (multipart/form-data):**
```
file: <image_or_video_file>
confidence_threshold: float (default: 0.8)
max_detections: int (default: 10)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "detections": [
      {
        "license_plate": "ABC123",
        "confidence": 0.95,
        "bbox": {
          "x": 100,
          "y": 50,
          "width": 120,
          "height": 40
        },
        "region": "Lima",
        "country": "Peru"
      }
    ],
    "processing_time_ms": 150,
    "image_dimensions": {
      "width": 1920,
      "height": 1080
    }
  }
}
```

### POST /detect/license-plates/batch
Procesamiento en lote de múltiples archivos.

**Request (multipart/form-data):**
```
files: <array_of_files>
confidence_threshold: float
batch_size: int (default: 4)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "filename": "image1.jpg",
        "detections": [...],
        "status": "success"
      },
      {
        "filename": "image2.jpg",
        "error": "No license plates detected",
        "status": "no_detections"
      }
    ],
    "total_processed": 2,
    "total_detections": 3,
    "processing_time_ms": 450
  }
}
```

## Clasificación de Vehículos

### POST /classify/vehicles
Clasificar tipos de vehículos en imágenes.

**Request:**
```json
{
  "image_url": "string",
  "bbox": {
    "x": 100,
    "y": 50,
    "width": 200,
    "height": 150
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vehicle_type": "car",
    "confidence": 0.92,
    "predictions": [
      {
        "class": "car",
        "confidence": 0.92
      },
      {
        "class": "suv",
        "confidence": 0.06
      },
      {
        "class": "truck",
        "confidence": 0.02
      }
    ],
    "attributes": {
      "color": "white",
      "color_confidence": 0.88,
      "make": "toyota",
      "make_confidence": 0.75
    }
  }
}
```

## Detección de Infracciones

### POST /detect/infractions
Detectar infracciones de tráfico en video/imagen.

**Request:**
```json
{
  "media_url": "string",
  "media_type": "image|video",
  "location": {
    "latitude": -12.0464,
    "longitude": -77.0428
  },
  "traffic_rules": {
    "speed_limit": 60,
    "red_light_detection": true,
    "parking_zones": [...]
  },
  "detection_config": {
    "confidence_threshold": 0.8,
    "tracking_enabled": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "infractions": [
      {
        "type": "speeding",
        "severity": "high",
        "confidence": 0.94,
        "timestamp": "2024-01-15T14:30:15Z",
        "vehicle": {
          "license_plate": "ABC123",
          "type": "car",
          "bbox": [100, 50, 200, 150],
          "tracking_id": "track_001"
        },
        "evidence": {
          "speed_detected": 85,
          "speed_limit": 60,
          "measurement_method": "optical_flow",
          "frames": [
            {
              "timestamp": "2024-01-15T14:30:14Z",
              "bbox": [95, 48, 198, 148]
            },
            {
              "timestamp": "2024-01-15T14:30:15Z", 
              "bbox": [100, 50, 200, 150]
            }
          ]
        }
      }
    ],
    "processing_time_ms": 2500,
    "total_vehicles_detected": 5,
    "total_infractions": 1
  }
}
```

### POST /detect/infractions/realtime
Stream de detección en tiempo real (WebSocket).

**WebSocket Connection:** `/ws/detect/realtime`

**Message Format:**
```json
{
  "type": "frame",
  "data": "base64_encoded_image",
  "timestamp": "2024-01-15T14:30:00Z",
  "camera_id": "cam_001"
}
```

**Response Format:**
```json
{
  "type": "detection",
  "camera_id": "cam_001",
  "timestamp": "2024-01-15T14:30:00Z",
  "detections": [...],
  "infractions": [...]
}
```

## Análisis de Tráfico

### POST /analyze/traffic-flow
Analizar flujo de tráfico en un video.

**Request:**
```json
{
  "video_url": "string",
  "analysis_type": "flow|density|speed",
  "roi": {
    "polygons": [
      {
        "name": "lane_1",
        "points": [[100, 200], [300, 200], [350, 400], [50, 400]]
      }
    ]
  },
  "time_window": "5m"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "traffic_flow": {
      "lane_1": {
        "vehicle_count": 45,
        "avg_speed": 55.5,
        "density": "medium",
        "flow_rate": "540 vehicles/hour"
      }
    },
    "time_series": [
      {
        "timestamp": "2024-01-15T14:30:00Z",
        "vehicle_count": 8,
        "avg_speed": 58.2
      }
    ],
    "anomalies": [
      {
        "type": "congestion",
        "timestamp": "2024-01-15T14:35:00Z",
        "severity": "medium",
        "description": "Traffic jam detected in lane_1"
      }
    ]
  }
}
```

## Gestión de Modelos

### GET /models
Listar modelos disponibles.

**Response:**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "name": "license_plate_detection",
        "version": "v2.1",
        "status": "active",
        "accuracy": 0.98,
        "size_mb": 125.5,
        "last_updated": "2024-01-10T00:00:00Z",
        "supported_regions": ["LATAM", "US", "EU"]
      },
      {
        "name": "vehicle_classification", 
        "version": "v1.5",
        "status": "active",
        "accuracy": 0.95,
        "size_mb": 89.2,
        "classes": ["car", "truck", "motorcycle", "bus", "bicycle"]
      }
    ]
  }
}
```

### POST /models/{model_name}/reload
Recargar modelo específico.

### GET /models/{model_name}/performance
Obtener métricas de performance de un modelo.

**Response:**
```json
{
  "success": true,
  "data": {
    "model_name": "license_plate_detection",
    "version": "v2.1",
    "metrics": {
      "accuracy": 0.98,
      "precision": 0.97,
      "recall": 0.96,
      "f1_score": 0.965,
      "inference_time_ms": {
        "avg": 85,
        "p50": 82,
        "p95": 120,
        "p99": 150
      }
    },
    "test_dataset": {
      "size": 10000,
      "last_evaluated": "2024-01-10T00:00:00Z"
    }
  }
}
```

## Configuración

### GET /config
Obtener configuración actual del servicio ML.

**Response:**
```json
{
  "success": true,
  "data": {
    "detection": {
      "confidence_threshold": 0.8,
      "nms_threshold": 0.4,
      "max_detections": 100
    },
    "classification": {
      "top_k": 5,
      "confidence_threshold": 0.7
    },
    "processing": {
      "batch_size": 4,
      "max_image_size": 2048,
      "gpu_enabled": true,
      "max_concurrent_requests": 10
    },
    "models": {
      "auto_update": false,
      "cache_enabled": true,
      "warm_up_on_start": true
    }
  }
}
```

### PUT /config
Actualizar configuración.

**Request:**
```json
{
  "detection": {
    "confidence_threshold": 0.85
  },
  "processing": {
    "batch_size": 8,
    "max_concurrent_requests": 15
  }
}
```

## Procesamiento de Video

### POST /video/process
Procesar video completo para detección de infracciones.

**Request:**
```json
{
  "video_url": "string",
  "output_format": "json|video|both",
  "processing_options": {
    "frame_skip": 2,
    "output_video": true,
    "annotations": true,
    "track_vehicles": true
  },
  "callback_url": "string"
}
```

**Response (Async):**
```json
{
  "success": true,
  "data": {
    "job_id": "job_12345",
    "status": "queued",
    "estimated_completion": "2024-01-15T14:45:00Z",
    "webhook_url": "string"
  }
}
```

### GET /video/jobs/{job_id}
Obtener estado de procesamiento de video.

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job_12345",
    "status": "completed",
    "progress": 100,
    "started_at": "2024-01-15T14:30:00Z",
    "completed_at": "2024-01-15T14:42:30Z",
    "results": {
      "total_frames": 1800,
      "processed_frames": 1800,
      "detections": 125,
      "infractions": 8,
      "output_urls": {
        "annotated_video": "/results/job_12345/output.mp4",
        "detections_json": "/results/job_12345/detections.json"
      }
    }
  }
}
```

## Calibración de Cámaras

### POST /calibrate/camera
Calibrar cámara para mediciones precisas.

**Request:**
```json
{
  "camera_id": "string",
  "calibration_images": ["url1", "url2", "url3"],
  "reference_objects": [
    {
      "type": "lane_marking",
      "real_length_meters": 3.0,
      "pixel_coordinates": [[100, 200], [400, 200]]
    }
  ],
  "camera_parameters": {
    "height_meters": 6.0,
    "angle_degrees": 15.0,
    "focal_length": 50.0
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "calibration_id": "cal_12345",
    "camera_id": "cam_001",
    "homography_matrix": [[1.2, 0.1, -50], [0.05, 1.1, -30], [0.0001, 0.0002, 1]],
    "pixels_per_meter": 15.5,
    "accuracy_score": 0.96,
    "valid_until": "2024-04-15T14:30:00Z"
  }
}
```

## Métricas y Monitoreo

### GET /metrics/prometheus
Métricas en formato Prometheus.

**Métricas Disponibles:**
- `ml_requests_total`: Total de requests procesados
- `ml_request_duration_seconds`: Duración de requests
- `ml_model_accuracy`: Precisión de modelos
- `ml_gpu_utilization`: Utilización de GPU
- `ml_memory_usage_bytes`: Uso de memoria
- `ml_inference_time_seconds`: Tiempo de inferencia

### GET /stats
Estadísticas generales del servicio.

**Response:**
```json
{
  "success": true,
  "data": {
    "uptime_seconds": 86400,
    "total_requests": 15420,
    "successful_requests": 15180,
    "failed_requests": 240,
    "average_response_time_ms": 125.5,
    "models_loaded": 3,
    "gpu_memory_used": "3.2GB",
    "cpu_usage_percent": 45.2,
    "requests_per_minute": {
      "current": 25,
      "peak": 85,
      "average": 35
    }
  }
}
```

## Códigos de Error Específicos

### 422 Model Error
```json
{
  "success": false,
  "error_code": "MODEL_ERROR",
  "message": "Error en el modelo de ML",
  "details": {
    "model": "license_plate_detection",
    "error": "CUDA out of memory"
  }
}
```

### 429 Rate Limit
```json
{
  "success": false,
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Límite de requests excedido",
  "retry_after": 60
}
```

### 507 Insufficient Storage
```json
{
  "success": false,
  "error_code": "INSUFFICIENT_STORAGE",
  "message": "Espacio insuficiente para procesar el archivo"
}
```

## Rate Limiting

- **Detección básica**: 100 requests/minuto
- **Procesamiento de video**: 5 requests/minuto  
- **Análisis en lote**: 10 requests/minuto
- **WebSocket**: 1000 mensajes/minuto

## Formatos Soportados

### Imágenes
- JPEG, PNG, WEBP, TIFF
- Tamaño máximo: 50MB
- Resolución máxima: 8K (7680x4320)

### Videos
- MP4, AVI, MOV, MKV
- Tamaño máximo: 2GB
- Duración máxima: 60 minutos
- Codecs: H.264, H.265, VP9

## SDK y Ejemplos

### Python Client
```python
import requests
from trafficsystem_ml import MLClient

client = MLClient("http://localhost:8001")

# Detectar placas
with open("image.jpg", "rb") as f:
    result = client.detect_license_plates(f)
    
# Análisis de infracciones
result = client.detect_infractions(
    video_url="video.mp4",
    speed_limit=60
)
```

### JavaScript Client
```javascript
const MLClient = require('trafficsystem-ml-client');

const client = new MLClient('http://localhost:8001');

// Upload y detección
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await client.detectLicensePlates(formData);
```

## Desarrollo y Testing

### Ambiente de Desarrollo
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Tests
pytest tests/ -v
```

### Mock para Testing
```python
# Test client
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```