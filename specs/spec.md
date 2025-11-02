# Especificación Técnica - Sistema de Detección de Infracciones de Tránsito

## 1. Arquitectura del Sistema

### 1.1 Vista General

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAPA DE PRESENTACIÓN                         │
├─────────────────────────────────────────────────────────────────────┤
│  Django Admin Panel  │  Web Dashboard  │  Mobile App (Future)       │
│  (Operadores)        │  (Supervisores) │                            │
└──────────────┬───────────────────────────────────────────────────┬──┘
               │                                                   │
        ┌──────▼─────────────────────────────────────────────────▼─────┐
        │              API GATEWAY (Nginx + Kong/Traefik)              │
        │         Authentication │ Rate Limiting │ Routing              │
        └──────┬─────────────────────────────────────────────────┬─────┘
               │                                                  │
     ┌─────────▼─────────┐                          ┌────────────▼──────┐
     │  DJANGO BACKEND   │                          │  FASTAPI SERVICE  │
     │  (Admin Service)  │                          │ (Inference Engine)│
     ├───────────────────┤                          ├───────────────────┤
     │ • User Management │                          │ • Video Streaming │
     │ • CRUD Operations │                          │ • Object Detection│
     │ • Reports         │                          │ • OCR Processing  │
     │ • Device Control  │◄────RabbitMQ/Kafka──────►│ • Event Publisher│
     │ • Authentication  │                          │ • Real-time API   │
     └─────────┬─────────┘                          └────────┬──────────┘
               │                                             │
               │         ┌───────────────────────┐           │
               └────────►│  PostgreSQL 16        │◄──────────┘
                         │  + PostGIS            │
                         │  + TimescaleDB        │
                         └───────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
         ┌──────────▼────┐  ┌───────▼──────┐  ┌─────▼────────┐
         │  Redis Cache  │  │ MinIO/S3     │  │  MLflow      │
         │  (Sessions)   │  │ (Videos)     │  │  (ML Models) │
         └───────────────┘  └──────────────┘  └──────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        CAPA DE IoT / EDGE                            │
├─────────────────────────────────────────────────────────────────────┤
│  EZVIZ H6C Pro 2K (Camera #1...N)                                   │
│  ├─ RTSP Stream ────────────────────┐                               │
│  ├─ ONVIF Control ◄─────────────────┤                               │
│  └─ Local Storage (Backup) ─────────┤                               │
│                                      │                               │
│  ┌───────────────────────────────────▼───────────────────┐          │
│  │       Edge Processing Unit (Optional)                  │          │
│  │  • NVIDIA Jetson Nano/Xavier (GPU)                     │          │
│  │  • Local YOLO Inference (reduce bandwidth)             │          │
│  │  • Event-based upload (only infractions)               │          │
│  └────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   CAPA DE MONITOREO & OPS                            │
├─────────────────────────────────────────────────────────────────────┤
│  Prometheus │ Grafana │ ELK Stack │ Jaeger │ Sentry                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Arquitectura de Microservicios

#### 1.2.1 Django Admin Service
**Responsabilidades:**
- Gestión de usuarios y autenticación (Django Auth + JWT).
- CRUD de entidades: devices, zones, drivers, vehicles, infractions.
- Generación de reportes (PDF, Excel).
- Panel administrativo con Django Admin.
- API REST para consumo por frontend.

**Tecnologías:**
- Django 5.0, Django REST Framework 3.14
- Gunicorn + Uvicorn workers
- PostgreSQL (SQLAlchemy ORM opcional para queries complejas)

**Endpoints Principales:**
```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/users/
POST   /api/devices/
GET    /api/infractions/?status=pending&date=2025-11-01
GET    /api/reports/daily?zone=ZN001
POST   /api/vehicles/{plate}/enrich  # Consulta SUNARP
```

#### 1.2.2 FastAPI Inference Service
**Responsabilidades:**
- Recepción de streams RTSP desde cámaras IoT.
- Pipeline de inferencia:
  1. Decodificación de video (OpenCV, FFmpeg).
  2. Detección de vehículos con YOLOv8.
  3. Tracking de objetos con DeepSort.
  4. Detección y OCR de placas.
  5. Clasificación de infracciones.
- Publicación de eventos a RabbitMQ/Kafka.
- Almacenamiento de evidencia en MinIO.

**Tecnologías:**
- FastAPI 0.110, Uvicorn
- OpenCV 4.8, FFmpeg
- Ultralytics YOLOv8, ONNX Runtime
- PaddleOCR / EasyOCR

**Endpoints Principales:**
```
POST   /api/inference/stream/start  # Inicia procesamiento de cámara
POST   /api/inference/stream/stop
GET    /api/inference/cameras/{id}/status
GET    /api/inference/events?camera_id=CAM001&limit=100
WS     /ws/stream/{camera_id}  # WebSocket para streaming en tiempo real
```

#### 1.2.3 ML Service (Predictive Analytics)
**Responsabilidades:**
- Entrenamiento de modelos predictivos (XGBoost, LSTM).
- Inferencia de riesgo de reincidencia y accidentes.
- Gestión de versiones de modelos con MLflow.
- Monitoreo de drift de datos.

**Tecnologías:**
- FastAPI (APIs de predicción)
- XGBoost, LightGBM, TensorFlow
- MLflow, Optuna (hyperparameter tuning)
- Celery para entrenamiento asíncrono

**Endpoints:**
```
POST   /api/ml/predict/recidivism  # Predicción de reincidencia
POST   /api/ml/predict/risk-score  # Score de riesgo conductor
POST   /api/ml/models/train  # Trigger entrenamiento
GET    /api/ml/models/versions  # Listar versiones de modelos
```

#### 1.2.4 Background Workers (Celery)
**Tareas Asíncronas:**
- Consulta a API SUNARP (batch processing).
- Generación de reportes complejos (PDF con gráficos).
- Limpieza de datos antiguos (retention policies).
- Reentrenamiento periódico de modelos ML.
- Notificaciones por email/SMS (opcional).

### 1.3 Flujo Funcional End-to-End

#### Escenario: Detección de Exceso de Velocidad

```
1. [Cámara IoT] EZVIZ H6C captura video a 30 fps, transmite via RTSP
   └─> rtsp://admin:pass@192.168.1.100:554/h264/ch1/main/av_stream

2. [FastAPI Inference] Recibe stream y decodifica frames
   └─> cv2.VideoCapture(rtsp_url)

3. [YOLOv8] Detecta vehículos en frame
   └─> model.predict(frame) → bounding boxes de vehículos

4. [DeepSort] Tracking de objetos, asigna ID único por vehículo
   └─> tracker.update(detections) → track_id=12345, bbox, velocity_vector

5. [Speed Calculation] Calcula velocidad mediante homografía y tiempo entre frames
   └─> speed = distance_pixels * calibration_factor / delta_time
   └─> Si speed > 60 km/h (límite de zona) → INFRACCIÓN

6. [Plate Detection] Detecta región de placa en vehículo infractor
   └─> plate_detector.predict(vehicle_crop) → plate_bbox

7. [OCR] Extrae caracteres de placa
   └─> ocr.recognize(plate_crop) → "ABC-1234" (confidence 0.92)

8. [Event Generation] Crea evento de infracción
   └─> {
         "type": "SPEED_VIOLATION",
         "plate": "ABC-1234",
         "speed": 78.5,
         "limit": 60,
         "timestamp": "2025-11-01T14:35:22Z",
         "camera_id": "CAM001",
         "evidence": {
           "video_clip": "s3://bucket/2025/11/01/CAM001_143522.mp4",
           "snapshot": "s3://bucket/2025/11/01/CAM001_143522.jpg"
         }
       }

9. [MinIO] Almacena video clip (10 seg antes + 5 seg después) y snapshot
   └─> minio_client.put_object(bucket, key, video_buffer)

10. [RabbitMQ] Publica evento a cola de infracciones
    └─> channel.basic_publish(exchange='infractions', routing_key='speed', body=event_json)

11. [Django Consumer] Consume evento y persiste en PostgreSQL
    └─> Infraction.objects.create(...)

12. [SUNARP Enrichment] Celery task consulta API SUNARP
    └─> GET https://consultavehicular-sunarp.com/buscar/ABC-1234
    └─> Actualiza infraction.vehicle_owner, infraction.driver_details

13. [ML Prediction] Calcula score de riesgo del conductor
    └─> risk_score = ml_model.predict({
          "infraction_history": 3,
          "severity": "medium",
          "time_of_day": "afternoon",
          "recency": 7
        }) → 0.68 (alto riesgo)

14. [Notification] (Opcional) Envía notificación a operador
    └─> email_service.send(to=operator@municipalidad.pe, subject="Nueva infracción CAM001")

15. [Dashboard] Operador visualiza infracción en panel Django
    └─> Valida evidencia, confirma/rechaza infracción, genera multa
```

## 2. Modelo de Datos (PostgreSQL)

### 2.1 Esquema de Base de Datos

#### Tabla: `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'supervisor', 'operator', 'auditor')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);
```

#### Tabla: `zones`
```sql
CREATE TABLE zones (
    id VARCHAR(50) PRIMARY KEY,  -- Ejemplo: ZN001
    name VARCHAR(255) NOT NULL,
    description TEXT,
    speed_limit INTEGER NOT NULL,  -- km/h
    geometry GEOGRAPHY(POLYGON, 4326),  -- PostGIS para geolocalización
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_zones_geometry ON zones USING GIST(geometry);
```

#### Tabla: `devices` (Cámaras)
```sql
CREATE TABLE devices (
    id VARCHAR(50) PRIMARY KEY,  -- Ejemplo: CAM001
    zone_id VARCHAR(50) REFERENCES zones(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(100) DEFAULT 'EZVIZ H6C Pro 2K',
    rtsp_url TEXT NOT NULL,  -- rtsp://user:pass@ip:port/path
    onvif_url TEXT,
    location GEOGRAPHY(POINT, 4326),  -- Coordenadas GPS
    orientation FLOAT,  -- Ángulo de orientación (0-360°)
    calibration_matrix JSONB,  -- Matriz de homografía para cálculo de velocidad
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'error')),
    last_heartbeat TIMESTAMP,
    metadata JSONB,  -- Configuración adicional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_devices_zone ON devices(zone_id);
CREATE INDEX idx_devices_status ON devices(status);
```

#### Tabla: `vehicles`
```sql
CREATE TABLE vehicles (
    plate VARCHAR(20) PRIMARY KEY,  -- ABC-1234
    brand VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    color VARCHAR(50),
    vehicle_type VARCHAR(50),  -- sedan, suv, truck, motorcycle
    owner_name VARCHAR(255),
    owner_dni VARCHAR(20),
    owner_address TEXT,
    registration_date DATE,
    sunarp_last_check TIMESTAMP,  -- Última consulta a SUNARP
    sunarp_data JSONB,  -- Datos completos de SUNARP
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vehicles_owner_dni ON vehicles(owner_dni);
```

#### Tabla: `drivers`
```sql
CREATE TABLE drivers (
    dni VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    license_number VARCHAR(50),
    license_category VARCHAR(20),
    license_expiry DATE,
    birth_date DATE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    risk_score FLOAT DEFAULT 0.0,  -- Score ML de riesgo (0-1)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_drivers_risk_score ON drivers(risk_score DESC);
```

#### Tabla: `infractions`
```sql
CREATE TABLE infractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    infraction_code VARCHAR(50) NOT NULL,  -- Código interno (INF-20251101-001)
    type VARCHAR(50) NOT NULL CHECK (type IN ('SPEED_VIOLATION', 'LANE_INVASION', 'RED_LIGHT', 'OTHER')),
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE SET NULL,
    zone_id VARCHAR(50) REFERENCES zones(id) ON DELETE SET NULL,
    plate VARCHAR(20) REFERENCES vehicles(plate) ON DELETE SET NULL,
    driver_dni VARCHAR(20) REFERENCES drivers(dni) ON DELETE SET NULL,
    
    -- Detalles de la infracción
    detected_speed FLOAT,  -- km/h (para exceso de velocidad)
    speed_limit FLOAT,
    violation_details JSONB,  -- Información adicional específica por tipo
    
    -- Evidencia multimedia
    video_url TEXT NOT NULL,  -- s3://bucket/path/to/video.mp4
    snapshot_url TEXT NOT NULL,  -- s3://bucket/path/to/snapshot.jpg
    
    -- Metadatos de detección
    confidence_score FLOAT,  -- Confianza del modelo (0-1)
    ocr_confidence FLOAT,  -- Confianza del OCR en placa
    
    -- Estado y seguimiento
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'validated', 'rejected', 'appealed', 'paid')),
    validated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    validated_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Predicciones ML
    recidivism_risk FLOAT,  -- Probabilidad de reincidencia (0-1)
    accident_risk FLOAT,  -- Probabilidad de accidente (0-1)
    
    detected_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_infractions_type ON infractions(type);
CREATE INDEX idx_infractions_status ON infractions(status);
CREATE INDEX idx_infractions_device ON infractions(device_id);
CREATE INDEX idx_infractions_plate ON infractions(plate);
CREATE INDEX idx_infractions_detected_at ON infractions(detected_at DESC);
CREATE INDEX idx_infractions_zone_date ON infractions(zone_id, detected_at);
```

#### Tabla: `ml_models`
```sql
CREATE TABLE ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,  -- recidivism_xgboost, accident_lstm
    version VARCHAR(50) NOT NULL,  -- v1.2.3
    model_type VARCHAR(50),  -- classification, regression
    framework VARCHAR(50),  -- xgboost, tensorflow, pytorch
    
    -- Artefactos del modelo
    model_path TEXT NOT NULL,  -- s3://models/recidivism_v1.2.3.pkl
    mlflow_run_id VARCHAR(100),
    
    -- Métricas de rendimiento
    metrics JSONB,  -- {accuracy: 0.92, precision: 0.89, recall: 0.87}
    hyperparameters JSONB,
    
    -- Deployment
    is_active BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP,
    deployed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(model_name, version)
);

CREATE INDEX idx_ml_models_active ON ml_models(model_name, is_active);
```

#### Tabla: `events` (Time-Series con TimescaleDB)
```sql
CREATE TABLE events (
    id BIGSERIAL,
    event_type VARCHAR(50) NOT NULL,  -- detection, tracking, ocr, inference_time
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    data JSONB,  -- Payload del evento
    PRIMARY KEY (id, timestamp)
);

-- Convertir a hypertable de TimescaleDB
SELECT create_hypertable('events', 'timestamp');

-- Política de retención: mantener últimos 90 días
SELECT add_retention_policy('events', INTERVAL '90 days');

CREATE INDEX idx_events_device_time ON events(device_id, timestamp DESC);
CREATE INDEX idx_events_type ON events(event_type);
```

#### Tabla: `inference_metrics` (Monitoreo de rendimiento)
```sql
CREATE TABLE inference_metrics (
    id BIGSERIAL,
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Métricas de inferencia
    fps FLOAT,  -- Frames procesados por segundo
    latency_ms FLOAT,  -- Latencia por frame
    gpu_utilization FLOAT,  -- % de uso de GPU
    cpu_utilization FLOAT,
    memory_mb FLOAT,
    
    -- Detecciones
    detections_count INTEGER,  -- Objetos detectados en frame
    infractions_count INTEGER,  -- Infracciones detectadas
    
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('inference_metrics', 'timestamp');
CREATE INDEX idx_inference_metrics_device ON inference_metrics(device_id, timestamp DESC);
```

### 2.2 Relaciones y Cardinalidad

```
zones (1) ──< (N) devices
zones (1) ──< (N) infractions
devices (1) ──< (N) infractions
devices (1) ──< (N) events
vehicles (1) ──< (N) infractions
drivers (1) ──< (N) infractions
users (1) ──< (N) infractions (validación)
ml_models (1) ──< (N) infractions (predicción)
```

## 3. Especificación de APIs

### 3.1 Django Admin API (REST)

#### Autenticación
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "operator01",
  "password": "SecureP@ss123"
}

Response 200 OK:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "operator01",
    "email": "operator@municipalidad.pe",
    "role": "operator"
  }
}
```

#### Gestión de Infracciones
```http
GET /api/infractions/?status=pending&limit=50&offset=0
Authorization: Bearer <token>

Response 200 OK:
{
  "count": 127,
  "next": "/api/infractions/?status=pending&limit=50&offset=50",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "infraction_code": "INF-20251101-001",
      "type": "SPEED_VIOLATION",
      "device_id": "CAM001",
      "zone_id": "ZN001",
      "plate": "ABC-1234",
      "detected_speed": 78.5,
      "speed_limit": 60.0,
      "confidence_score": 0.92,
      "ocr_confidence": 0.89,
      "snapshot_url": "https://storage.example.com/snapshots/2025/11/01/CAM001_143522.jpg",
      "video_url": "https://storage.example.com/videos/2025/11/01/CAM001_143522.mp4",
      "status": "pending",
      "detected_at": "2025-11-01T14:35:22Z",
      "recidivism_risk": 0.68
    }
    // ... más infracciones
  ]
}
```

```http
PUT /api/infractions/{id}/validate
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "validated",
  "notes": "Infracción confirmada, evidencia clara"
}

Response 200 OK:
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "validated",
  "validated_by": "550e8400-e29b-41d4-a716-446655440000",
  "validated_at": "2025-11-01T15:20:00Z"
}
```

#### Enriquecimiento de Datos (SUNARP)
```http
POST /api/vehicles/{plate}/enrich
Authorization: Bearer <token>

Response 200 OK:
{
  "plate": "ABC-1234",
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2020,
  "color": "Gris",
  "owner_name": "JUAN CARLOS PEREZ LOPEZ",
  "owner_dni": "12345678",
  "registration_date": "2020-03-15",
  "sunarp_last_check": "2025-11-01T15:25:00Z"
}
```

#### Reportes
```http
GET /api/reports/daily?date=2025-11-01&zone_id=ZN001
Authorization: Bearer <token>

Response 200 OK:
{
  "date": "2025-11-01",
  "zone_id": "ZN001",
  "zone_name": "Av. Javier Prado - San Isidro",
  "total_infractions": 34,
  "by_type": {
    "SPEED_VIOLATION": 22,
    "LANE_INVASION": 8,
    "RED_LIGHT": 4
  },
  "by_hour": [
    {"hour": 0, "count": 0},
    {"hour": 1, "count": 0},
    // ...
    {"hour": 14, "count": 8},
    {"hour": 15, "count": 12},
    // ...
  ],
  "top_violators": [
    {"plate": "ABC-1234", "count": 3},
    {"plate": "XYZ-9876", "count": 2}
  ],
  "average_speed_violation": 72.3,
  "export_url": "/api/reports/daily/2025-11-01/ZN001/export?format=pdf"
}
```

### 3.2 FastAPI Inference API

#### Iniciar Procesamiento de Cámara
```http
POST /api/inference/stream/start
Content-Type: application/json
Authorization: Bearer <token>

{
  "device_id": "CAM001",
  "rtsp_url": "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream",
  "config": {
    "fps": 30,
    "resolution": "2K",
    "detection_threshold": 0.5,
    "speed_limit": 60
  }
}

Response 200 OK:
{
  "device_id": "CAM001",
  "status": "streaming",
  "stream_id": "stream_CAM001_20251101_153000",
  "started_at": "2025-11-01T15:30:00Z"
}
```

#### Consultar Estado de Cámara
```http
GET /api/inference/cameras/CAM001/status
Authorization: Bearer <token>

Response 200 OK:
{
  "device_id": "CAM001",
  "status": "streaming",
  "uptime_seconds": 3600,
  "fps": 29.8,
  "latency_ms": 187,
  "detections_count": 1247,
  "infractions_count": 12,
  "last_frame_at": "2025-11-01T16:29:59Z",
  "health": "healthy"
}
```

#### WebSocket para Streaming en Tiempo Real
```javascript
// Cliente JavaScript
const ws = new WebSocket('ws://inference-api.example.com/ws/stream/CAM001?token=<jwt>');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Frame:', data.frame_id, 'Detections:', data.detections);
  
  // data = {
  //   "frame_id": 12345,
  //   "timestamp": "2025-11-01T16:30:00.123Z",
  //   "detections": [
  //     {
  //       "class": "car",
  //       "bbox": [120, 340, 450, 680],
  //       "confidence": 0.92,
  //       "track_id": 12345,
  //       "speed": 45.3
  //     }
  //   ],
  //   "infractions": [
  //     {
  //       "type": "SPEED_VIOLATION",
  //       "track_id": 12345,
  //       "plate": "ABC-1234",
  //       "speed": 78.5
  //     }
  //   ]
  // }
};
```

### 3.3 ML Service API

#### Predicción de Riesgo de Reincidencia
```http
POST /api/ml/predict/recidivism
Content-Type: application/json
Authorization: Bearer <token>

{
  "driver_dni": "12345678",
  "infraction_history": [
    {"type": "SPEED_VIOLATION", "date": "2025-10-15", "severity": "medium"},
    {"type": "RED_LIGHT", "date": "2025-09-22", "severity": "high"},
    {"type": "SPEED_VIOLATION", "date": "2025-08-10", "severity": "low"}
  ],
  "current_infraction": {
    "type": "SPEED_VIOLATION",
    "speed": 78.5,
    "limit": 60,
    "time_of_day": "afternoon",
    "weather": "clear"
  }
}

Response 200 OK:
{
  "driver_dni": "12345678",
  "recidivism_probability": 0.72,
  "risk_category": "high",
  "factors": [
    {"factor": "infraction_count", "importance": 0.35, "value": 3},
    {"factor": "recency", "importance": 0.28, "value": 15},
    {"factor": "severity_avg", "importance": 0.22, "value": "medium"}
  ],
  "model_version": "recidivism_xgboost_v1.2.3",
  "prediction_timestamp": "2025-11-01T16:35:00Z"
}
```

## 4. Pipeline de Inferencia Detallado

### 4.1 Componentes del Pipeline

```python
# Pseudocódigo del Pipeline de Inferencia

class InferencePipeline:
    def __init__(self, device_id, rtsp_url, config):
        self.device_id = device_id
        self.rtsp_url = rtsp_url
        self.config = config
        
        # Modelos
        self.vehicle_detector = YOLOv8("models/yolov8x.onnx")
        self.plate_detector = YOLOv8("models/plate_detector.onnx")
        self.ocr = PaddleOCR(lang='en')
        self.tracker = DeepSort()
        
        # Calibración
        self.homography_matrix = load_calibration(device_id)
        
    def process_stream(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                handle_stream_error()
                continue
            
            # 1. Detección de vehículos
            detections = self.vehicle_detector.predict(frame)
            # detections = [{class: 'car', bbox: [x1,y1,x2,y2], conf: 0.92}, ...]
            
            # 2. Tracking de objetos
            tracks = self.tracker.update(detections, frame)
            # tracks = [{track_id: 12345, bbox: [...], trajectory: [...], velocity: [vx, vy]}, ...]
            
            # 3. Análisis de infracciones por tipo
            for track in tracks:
                # 3a. Exceso de Velocidad
                speed_kmh = self.calculate_speed(track)
                if speed_kmh > self.config['speed_limit']:
                    self.handle_speed_violation(track, speed_kmh, frame)
                
                # 3b. Invasión de Carril
                if self.detect_lane_invasion(track):
                    self.handle_lane_invasion(track, frame)
                
                # 3c. Paso con Luz Roja
                if self.detect_red_light_violation(track):
                    self.handle_red_light(track, frame)
            
            frame_count += 1
    
    def calculate_speed(self, track):
        # Obtener trayectoria de últimos N frames
        trajectory = track['trajectory'][-10:]  # Últimos 10 frames
        
        # Transformar píxeles a coordenadas reales mediante homografía
        world_coords = []
        for point in trajectory:
            world_point = cv2.perspectiveTransform(
                np.array([[point]], dtype=np.float32),
                self.homography_matrix
            )
            world_coords.append(world_point[0][0])
        
        # Calcular distancia recorrida (en metros)
        total_distance = 0
        for i in range(1, len(world_coords)):
            distance = np.linalg.norm(world_coords[i] - world_coords[i-1])
            total_distance += distance
        
        # Calcular tiempo transcurrido
        time_seconds = len(trajectory) / self.config['fps']
        
        # Velocidad = distancia / tiempo (convertir m/s a km/h)
        speed_kmh = (total_distance / time_seconds) * 3.6
        
        return speed_kmh
    
    def handle_speed_violation(self, track, speed_kmh, frame):
        # 1. Detectar placa
        vehicle_crop = crop_bbox(frame, track['bbox'])
        plate_detection = self.plate_detector.predict(vehicle_crop)
        
        if not plate_detection:
            return  # No se detectó placa
        
        # 2. OCR de placa
        plate_crop = crop_bbox(vehicle_crop, plate_detection[0]['bbox'])
        plate_text, ocr_conf = self.ocr.recognize(plate_crop)
        
        if ocr_conf < 0.7:
            return  # Confianza muy baja
        
        # 3. Generar clip de video (10 seg antes + 5 seg después)
        video_clip = extract_video_clip(track, duration=15)
        
        # 4. Capturar snapshot
        snapshot = frame.copy()
        draw_bbox(snapshot, track['bbox'])
        draw_text(snapshot, f"Speed: {speed_kmh:.1f} km/h", track['bbox'])
        
        # 5. Almacenar evidencia en MinIO
        video_url = upload_to_storage(video_clip, f"{self.device_id}_{timestamp}.mp4")
        snapshot_url = upload_to_storage(snapshot, f"{self.device_id}_{timestamp}.jpg")
        
        # 6. Crear evento de infracción
        event = {
            "type": "SPEED_VIOLATION",
            "device_id": self.device_id,
            "plate": plate_text,
            "detected_speed": speed_kmh,
            "speed_limit": self.config['speed_limit'],
            "confidence_score": track['confidence'],
            "ocr_confidence": ocr_conf,
            "video_url": video_url,
            "snapshot_url": snapshot_url,
            "detected_at": datetime.utcnow().isoformat(),
            "metadata": {
                "track_id": track['track_id'],
                "bbox": track['bbox'],
                "weather": get_weather_conditions(),
                "visibility": calculate_visibility(frame)
            }
        }
        
        # 7. Publicar evento a RabbitMQ
        publish_event("infractions.speed", event)
        
        # 8. Log para monitoreo
        logger.info(f"Speed violation detected: {plate_text} at {speed_kmh:.1f} km/h")
```

### 4.2 Calibración de Cámaras

```python
# Proceso de calibración para cálculo de velocidad

def calibrate_camera(device_id):
    """
    Proceso manual de calibración:
    1. Colocar marcadores de referencia en la vía (cada 10 metros)
    2. Capturar frame de referencia
    3. Anotar coordenadas pixel de marcadores
    4. Calcular matriz de homografía
    """
    
    # Puntos en imagen (píxeles)
    image_points = np.array([
        [120, 680],  # Marcador 1
        [450, 650],  # Marcador 2 (10m adelante)
        [780, 620],  # Marcador 3 (20m adelante)
        [1100, 590]  # Marcador 4 (30m adelante)
    ], dtype=np.float32)
    
    # Puntos en mundo real (metros)
    world_points = np.array([
        [0, 0],
        [10, 0],
        [20, 0],
        [30, 0]
    ], dtype=np.float32)
    
    # Calcular matriz de homografía
    H, _ = cv2.findHomography(image_points, world_points)
    
    # Guardar calibración
    save_calibration(device_id, H)
    
    return H
```

### 4.3 Optimización de Rendimiento

```python
# Optimizaciones para cumplir con <250ms por frame

# 1. Usar ONNX Runtime con TensorRT para inferencia en GPU
import onnxruntime as ort

session_options = ort.SessionOptions()
session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

providers = [
    ('TensorrtExecutionProvider', {
        'device_id': 0,
        'trt_max_workspace_size': 2147483648,  # 2GB
        'trt_fp16_enable': True
    }),
    'CUDAExecutionProvider'
]

session = ort.InferenceSession("yolov8x.onnx", sess_options=session_options, providers=providers)

# 2. Procesamiento por lotes (batch inference)
def batch_inference(frames, batch_size=4):
    batches = [frames[i:i+batch_size] for i in range(0, len(frames), batch_size)]
    results = []
    for batch in batches:
        results.extend(model.predict(batch))
    return results

# 3. Procesamiento asíncrono con multiprocessing
from multiprocessing import Process, Queue

def worker_process(input_queue, output_queue):
    model = load_model()
    while True:
        frame = input_queue.get()
        result = model.predict(frame)
        output_queue.put(result)

# 4. Skip frames en escenas estáticas (detección de movimiento)
def detect_motion(prev_frame, curr_frame, threshold=1000):
    diff = cv2.absdiff(prev_frame, curr_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    motion_pixels = np.sum(thresh > 0)
    return motion_pixels > threshold

# 5. Cache de resultados de OCR (placas recurrentes)
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_ocr(plate_crop_hash):
    return ocr.recognize(plate_crop)
```

## 5. Integración con SUNARP API

### 5.1 Cliente de SUNARP

```python
# sunarp_client.py

import requests
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import redis

@dataclass
class VehicleData:
    plate: str
    brand: str
    model: str
    year: int
    color: str
    owner_name: str
    owner_dni: str
    registration_date: str
    raw_data: Dict

class SUNARPClient:
    BASE_URL = "https://consultavehicular-sunarp.com"
    CACHE_TTL = 86400  # 24 horas
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MunicipalidadTrafficSystem/1.0',
            'Accept': 'application/json'
        })
    
    def get_vehicle_data(self, plate: str) -> Optional[VehicleData]:
        # Verificar cache
        cached = self._get_from_cache(plate)
        if cached:
            return cached
        
        # Consultar API
        try:
            response = self.session.get(
                f"{self.BASE_URL}/buscar/{plate}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            vehicle = self._parse_response(plate, data)
            
            # Guardar en cache
            self._save_to_cache(plate, vehicle)
            
            return vehicle
            
        except requests.RequestException as e:
            logger.error(f"SUNARP API error for plate {plate}: {e}")
            return None
    
    def _parse_response(self, plate: str, data: Dict) -> VehicleData:
        return VehicleData(
            plate=plate,
            brand=data.get('marca', 'Unknown'),
            model=data.get('modelo', 'Unknown'),
            year=int(data.get('anio', 0)),
            color=data.get('color', 'Unknown'),
            owner_name=data.get('propietario', {}).get('nombre', 'Unknown'),
            owner_dni=data.get('propietario', {}).get('dni', 'Unknown'),
            registration_date=data.get('fecha_inscripcion', ''),
            raw_data=data
        )
    
    def _get_from_cache(self, plate: str) -> Optional[VehicleData]:
        cached_json = self.redis.get(f"sunarp:{plate}")
        if cached_json:
            return VehicleData(**json.loads(cached_json))
        return None
    
    def _save_to_cache(self, plate: str, vehicle: VehicleData):
        self.redis.setex(
            f"sunarp:{plate}",
            self.CACHE_TTL,
            json.dumps(vehicle.__dict__)
        )

# Celery task para enriquecimiento asíncrono
from celery import shared_task

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enrich_vehicle_data(self, infraction_id: str, plate: str):
    try:
        sunarp = SUNARPClient(redis_client)
        vehicle_data = sunarp.get_vehicle_data(plate)
        
        if vehicle_data:
            # Actualizar vehículo en DB
            vehicle, created = Vehicle.objects.update_or_create(
                plate=plate,
                defaults={
                    'brand': vehicle_data.brand,
                    'model': vehicle_data.model,
                    'year': vehicle_data.year,
                    'color': vehicle_data.color,
                    'owner_name': vehicle_data.owner_name,
                    'owner_dni': vehicle_data.owner_dni,
                    'registration_date': vehicle_data.registration_date,
                    'sunarp_data': vehicle_data.raw_data,
                    'sunarp_last_check': datetime.utcnow()
                }
            )
            
            # Actualizar infracción
            Infraction.objects.filter(id=infraction_id).update(
                driver_dni=vehicle_data.owner_dni
            )
            
            logger.info(f"Enriched vehicle {plate} for infraction {infraction_id}")
        else:
            logger.warning(f"No data found for plate {plate}")
            
    except Exception as e:
        logger.error(f"Error enriching plate {plate}: {e}")
        raise self.retry(exc=e)
```

## 6. Modelo Predictivo de Riesgo

### 6.1 Feature Engineering

```python
# ml/feature_engineering.py

import pandas as pd
from datetime import datetime, timedelta

def extract_features(driver_dni: str) -> Dict:
    """
    Extrae features para modelo de predicción de reincidencia
    """
    
    # Consultar historial de infracciones
    infractions = Infraction.objects.filter(
        driver_dni=driver_dni
    ).order_by('-detected_at')
    
    if not infractions.exists():
        return get_default_features()
    
    df = pd.DataFrame(list(infractions.values()))
    
    features = {}
    
    # 1. Características históricas
    features['infraction_count_total'] = len(df)
    features['infraction_count_30d'] = len(df[df['detected_at'] > datetime.utcnow() - timedelta(days=30)])
    features['infraction_count_90d'] = len(df[df['detected_at'] > datetime.utcnow() - timedelta(days=90)])
    features['infraction_count_365d'] = len(df[df['detected_at'] > datetime.utcnow() - timedelta(days=365)])
    
    # 2. Por tipo de infracción
    features['speed_violations'] = len(df[df['type'] == 'SPEED_VIOLATION'])
    features['lane_invasions'] = len(df[df['type'] == 'LANE_INVASION'])
    features['red_light_violations'] = len(df[df['type'] == 'RED_LIGHT'])
    
    # 3. Severidad promedio
    features['avg_speed_excess'] = df[df['type'] == 'SPEED_VIOLATION']['detected_speed'].mean() - df['speed_limit'].mean() if 'detected_speed' in df else 0
    
    # 4. Recencia
    days_since_last = (datetime.utcnow() - df.iloc[0]['detected_at']).days
    features['days_since_last_infraction'] = days_since_last
    features['recency_score'] = 1 / (1 + days_since_last)  # Más reciente = mayor score
    
    # 5. Patrones temporales
    df['hour'] = df['detected_at'].dt.hour
    df['day_of_week'] = df['detected_at'].dt.dayofweek
    features['infractions_night'] = len(df[(df['hour'] >= 22) | (df['hour'] <= 6)])
    features['infractions_weekend'] = len(df[df['day_of_week'] >= 5])
    
    # 6. Tasa de reincidencia histórica
    if len(df) > 1:
        time_between = (df.iloc[0]['detected_at'] - df.iloc[-1]['detected_at']).days
        features['infraction_rate'] = len(df) / max(time_between, 1)
    else:
        features['infraction_rate'] = 0
    
    # 7. Características del conductor
    driver = Driver.objects.filter(dni=driver_dni).first()
    if driver:
        features['driver_age'] = (datetime.utcnow().year - driver.birth_date.year) if driver.birth_date else 0
        features['driver_risk_score'] = driver.risk_score
    else:
        features['driver_age'] = 0
        features['driver_risk_score'] = 0
    
    return features

# Ejemplo de features extraídas:
# {
#     'infraction_count_total': 5,
#     'infraction_count_30d': 2,
#     'speed_violations': 4,
#     'lane_invasions': 1,
#     'avg_speed_excess': 15.3,
#     'days_since_last_infraction': 7,
#     'recency_score': 0.125,
#     'infractions_night': 2,
#     'infractions_weekend': 1,
#     'infraction_rate': 0.0137,  # ~5 infracciones en 365 días
#     'driver_age': 35,
#     'driver_risk_score': 0.45
# }
```

### 6.2 Entrenamiento del Modelo

```python
# ml/train_model.py

import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
import mlflow
import mlflow.xgboost

def train_recidivism_model():
    mlflow.set_experiment("traffic_recidivism")
    
    with mlflow.start_run():
        # 1. Cargar datos de entrenamiento
        data = load_training_data()  # Historial de conductores con etiqueta de reincidencia
        X = data.drop(columns=['label', 'driver_dni'])
        y = data['label']  # 1 = reincidió en 90 días, 0 = no reincidió
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 2. Entrenar modelo XGBoost
        params = {
            'objective': 'binary:logistic',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        
        mlflow.log_params(params)
        
        model = xgb.XGBClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        # 3. Evaluar modelo
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        mlflow.log_metrics(metrics)
        
        # 4. Registrar modelo en MLflow
        mlflow.xgboost.log_model(
            model,
            "model",
            registered_model_name="recidivism_xgboost"
        )
        
        # 5. Guardar en base de datos
        model_version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        model_path = f"s3://models/recidivism_{model_version}.pkl"
        
        MLModel.objects.create(
            model_name="recidivism_xgboost",
            version=model_version,
            model_type="classification",
            framework="xgboost",
            model_path=model_path,
            mlflow_run_id=mlflow.active_run().info.run_id,
            metrics=metrics,
            hyperparameters=params,
            is_active=True
        )
        
        print(f"Model trained successfully: {model_version}")
        print(f"Metrics: {metrics}")
        
        return model, metrics
```

## 7. Despliegue con Docker & Kubernetes

### 7.1 Dockerfile - FastAPI Inference Service

```dockerfile
# inference-service/Dockerfile

FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Descargar modelos (o montar desde volumen)
RUN mkdir -p /app/models
COPY models/*.onnx /app/models/

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Ejecutar con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 7.2 Kubernetes Deployment - Inference Service

```yaml
# k8s/inference-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-service
  namespace: traffic-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inference-service
  template:
    metadata:
      labels:
        app: inference-service
    spec:
      containers:
      - name: inference
        image: traffic-system/inference-service:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: "1"
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: MINIO_ENDPOINT
          value: "minio-service:9000"
        - name: RABBITMQ_URL
          valueFrom:
            secretKeyRef:
              name: rabbitmq-secret
              key: url
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        - name: calibration
          mountPath: /app/calibration
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
      - name: calibration
        configMap:
          name: camera-calibration
      nodeSelector:
        gpu: "nvidia-rtx"
      tolerations:
      - key: "nvidia.com/gpu"
        operator: "Exists"
        effect: "NoSchedule"

---

apiVersion: v1
kind: Service
metadata:
  name: inference-service
  namespace: traffic-system
spec:
  selector:
    app: inference-service
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP

---

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference-hpa
  namespace: traffic-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: inference-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 8. Monitoreo y Observabilidad

### 8.1 Métricas de Prometheus

```python
# metrics.py

from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Contadores
infractions_detected = Counter(
    'infractions_detected_total',
    'Total number of infractions detected',
    ['type', 'device_id']
)

frames_processed = Counter(
    'frames_processed_total',
    'Total number of frames processed',
    ['device_id']
)

# Histogramas (distribución de latencias)
inference_latency = Histogram(
    'inference_latency_seconds',
    'Latency of inference pipeline',
    ['stage'],  # detection, tracking, ocr
    buckets=[0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5, 1.0]
)

# Gauges (valores instantáneos)
active_streams = Gauge(
    'active_streams',
    'Number of active camera streams'
)

gpu_utilization = Gauge(
    'gpu_utilization_percent',
    'GPU utilization percentage',
    ['gpu_id']
)

# Endpoint de métricas
from fastapi import Response

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

### 8.2 Dashboard de Grafana

```json
{
  "dashboard": {
    "title": "Traffic Inference System",
    "panels": [
      {
        "title": "Infractions per Hour",
        "targets": [
          {
            "expr": "rate(infractions_detected_total[1h])"
          }
        ]
      },
      {
        "title": "Inference Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "GPU Utilization",
        "targets": [
          {
            "expr": "gpu_utilization_percent"
          }
        ]
      },
      {
        "title": "Active Camera Streams",
        "targets": [
          {
            "expr": "active_streams"
          }
        ]
      }
    ]
  }
}
```

---

**Versión**: 1.0  
**Fecha**: 2025-11-01  
**Estado**: Aprobado
