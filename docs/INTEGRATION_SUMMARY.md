# Resumen de Cambios - Integración YOLOv8 y OCR

**Fecha**: 2 de Noviembre, 2025  
**Objetivo**: Reemplazar detección simulada con YOLOv8 real, integrar OCR para placas, y registrar infracciones en la base de datos.

## ✅ Cambios Completados

### 1. Servicio de Inferencia - Nuevas Dependencias

**Archivo**: `inference-service/requirements.txt`

**Paquetes añadidos**:
```txt
ultralytics==8.0.230    # YOLOv8 para detección de vehículos
easyocr==1.7.1          # OCR para lectura de placas
```

### 2. Configuración ML

**Archivo**: `inference-service/app/core/config.py`

**Nuevas variables**:
```python
# ML Model Configuration
YOLO_MODEL_PATH: str = "/app/models/yolov8n.pt"
YOLO_CONFIDENCE_THRESHOLD: float = 0.5
YOLO_IOU_THRESHOLD: float = 0.45
OCR_LANGUAGES: list = ['en']
OCR_GPU: bool = False

# Django Backend API
DJANGO_API_URL: str = "http://django:8000"
DJANGO_API_TIMEOUT: int = 30
```

### 3. Servicio de Modelos ML (NUEVO)

**Archivo**: `inference-service/app/services/model_service.py` (320 líneas)

**Clase**: `ModelService`

**Métodos principales**:

#### `initialize()`
- Inicializa YOLOv8 y EasyOCR
- Descarga automáticamente yolov8n.pt si no existe
- Verifica disponibilidad de GPU

#### `detect_vehicles(frame: np.ndarray)`
- Detección con YOLOv8
- Filtra clases: car (2), motorcycle (3), bus (5), truck (7)
- Retorna: lista de detecciones con bbox, confianza, clase

#### `detect_license_plate(frame: np.ndarray, bbox: Dict)`
- Recorta región del vehículo
- Aplica EasyOCR
- Valida formato Perú: AAA-123, AB-1234, A12-345
- Retorna: texto de placa y confianza

#### `estimate_speed(track: List[Dict], time_delta: float, calibration_data: Dict)`
- Calcula desplazamiento en píxeles
- Convierte a metros usando calibración
- Retorna: velocidad en km/h

### 4. Cliente API Django (NUEVO)

**Archivo**: `inference-service/app/services/django_api.py` (180 líneas)

**Clase**: `DjangoAPIService`

**Métodos principales**:

#### `create_infraction(data: Dict)`
```python
POST /api/infractions/
Body: {
    "infraction_type": "speed",
    "severity": "medium",
    "vehicle": UUID,
    "license_plate_detected": "ABC-123",
    "detected_speed": 85.5,
    "speed_limit": 60,
    "evidence_metadata": {...}
}
```

#### `get_or_create_vehicle(license_plate: str, vehicle_data: Dict)`
```python
# Busca vehículo existente
GET /api/vehicles/?license_plate={plate}

# Si no existe, crea nuevo
POST /api/vehicles/
Body: {
    "license_plate": "ABC-123",
    "vehicle_type": "car",
    "color": "red",
    ...
}
```

#### `get_device(device_code: str)` y `get_zone(zone_code: str)`
- Obtiene información de dispositivo/zona para asociar con infracciones

### 5. WebSocket con Detección Real

**Archivo**: `inference-service/app/api/websocket.py`

**Clase nueva**: `VehicleTracker`
- Mantiene historial de 30 frames por vehículo
- Calcula centroide para tracking
- Limpia tracks antiguos automáticamente

**Clase modificada**: `RealtimeDetector`

**Pipeline completo en `process_frame()`**:
```python
1. Decodificar frame base64 → np.ndarray
2. YOLOv8.detect_vehicles() → list[detections]
3. Para cada vehículo:
   a. OCR.detect_license_plate() → placa + confianza
   b. VehicleTracker.update() → historial de tracking
   c. ModelService.estimate_speed() → velocidad estimada
   d. Si velocidad > límite:
      - Detectar infracción de velocidad
      - _register_infraction() → crear en BD
4. Retornar detecciones al frontend
```

**Nuevo método**: `_register_infraction()`
```python
async def _register_infraction(
    self,
    infraction_type: str,
    vehicle_plate: str,
    vehicle_type: str,
    detected_speed: float,
    bbox: dict,
    ...
):
    # 1. Obtiene/crea vehículo
    vehicle = await django_api.get_or_create_vehicle(...)
    
    # 2. Obtiene device y zone
    device = await django_api.get_device(...)
    zone = await django_api.get_zone(...)
    
    # 3. Crea infracción
    infraction = await django_api.create_infraction({
        "infraction_type": infraction_type,
        "vehicle": vehicle["id"],
        "license_plate_detected": vehicle_plate,
        "detected_speed": detected_speed,
        "speed_limit": zone["speed_limit"],
        "evidence_metadata": {...}
    })
```

### 6. Inicialización de Modelos al Startup

**Archivo**: `inference-service/app/main.py`

**Función modificada**: `lifespan()`
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing ML models...")
    await model_service.initialize()
    logger.info("ML models initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ML models...")
    await model_service.shutdown()
```

### 7. Serializers Django para Infracciones

**Archivo**: `backend-django/infractions/serializers.py`

**Nuevo serializer**: `InfractionCreateSerializer`

**Características**:
```python
class InfractionCreateSerializer(serializers.ModelSerializer):
    # Campos opcionales con defaults
    device = serializers.UUIDField(required=False)
    zone = serializers.UUIDField(required=False)
    
    def validate(self, data):
        # Asigna device/zone por defecto si no se proporcionan
        if 'device' not in data:
            data['device'] = Device.objects.first().id
        if 'zone' not in data:
            data['zone'] = Zone.objects.first().id
        return data
    
    def create(self, validated_data):
        # Auto-genera código de infracción
        validated_data['infraction_code'] = (
            f"INF-{validated_data['infraction_type'].upper()[:3]}-"
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        return super().create(validated_data)
```

### 8. Views Django para Infracciones

**Archivo**: `backend-django/infractions/views.py`

**Modificación en**: `InfractionViewSet`

```python
def get_serializer_class(self):
    if self.action == 'create':
        return InfractionCreateSerializer
    return InfractionSerializer
```

Esto permite que el endpoint `POST /api/infractions/` use el nuevo serializer con las validaciones y auto-generación de código.

## 📊 Flujo de Datos Completo

```
┌─────────────────┐
│   FRONTEND      │
│  (Next.js)      │
└────────┬────────┘
         │ WebSocket (frame base64)
         ↓
┌─────────────────────────────────────┐
│   INFERENCE SERVICE (FastAPI)       │
│                                     │
│  ┌─────────────────────────────┐  │
│  │  RealtimeDetector           │  │
│  │  - process_frame()          │  │
│  └──────────┬──────────────────┘  │
│             │                      │
│  ┌──────────▼──────────┐          │
│  │  ModelService       │          │
│  │  - YOLOv8          │          │
│  │  - EasyOCR         │          │
│  │  - VehicleTracker  │          │
│  └──────────┬──────────┘          │
│             │                      │
│  ┌──────────▼──────────┐          │
│  │  DjangoAPIService   │          │
│  │  - HTTP Client      │          │
│  └──────────┬──────────┘          │
└─────────────┼───────────────────────┘
              │ HTTP POST
              ↓
┌─────────────────────────────────────┐
│   DJANGO BACKEND (REST API)         │
│                                     │
│  ┌─────────────────────────────┐  │
│  │  InfractionViewSet          │  │
│  │  - InfractionCreateSerializer│  │
│  └──────────┬──────────────────┘  │
│             │                      │
│  ┌──────────▼──────────┐          │
│  │  PostgreSQL         │          │
│  │  - infractions      │          │
│  │  - vehicles         │          │
│  │  - devices          │          │
│  │  - zones            │          │
│  └─────────────────────┘          │
└─────────────────────────────────────┘
```

## 🚀 Próximos Pasos

### 1. Build y Deploy (EN CURSO)
```bash
# Reconstruir servicio de inferencia
docker compose build inference

# Reiniciar servicio
docker compose up -d inference

# Verificar logs
docker compose logs -f inference
```

### 2. Testing End-to-End

1. **Verificar inicio de modelos**:
```bash
docker compose logs inference | grep "ML models initialized"
```

2. **Abrir interfaz**:
- Navegar a: http://localhost:3002
- Ir a "Monitoreo en Tiempo Real"

3. **Probar detección**:
- Seleccionar "Cámara Web Local"
- Configurar límite de velocidad: 60 km/h
- Habilitar todas las detecciones
- Click "Iniciar Detección"

4. **Verificar registro en BD**:
```bash
# Django Admin
http://localhost:8000/admin/infractions/infraction/

# API REST
curl http://localhost:8000/api/infractions/ | jq
```

### 3. Calibración

**Calibración de cámara** (para velocidad precisa):
```python
# En inference-service/app/core/config.py
CAMERA_CALIBRATION = {
    "meters_per_pixel": 0.05,  # Ajustar según altura de cámara
    "fps": 30,
    "focal_length": 4.0  # mm
}
```

**Cómo calibrar**:
1. Medir distancia real conocida (ej: 5 metros)
2. Contar píxeles en esa distancia
3. Calcular: `meters_per_pixel = distancia_real / píxeles`

### 4. Ajuste de Umbrales

**Confianza de detección**:
```python
# Más estricto (menos false positives)
YOLO_CONFIDENCE_THRESHOLD = 0.7

# Más permisivo (más detecciones)
YOLO_CONFIDENCE_THRESHOLD = 0.3
```

**Validez de placa OCR**:
```python
# En model_service.py, ajustar mínimo de confianza
if confidence > 0.6:  # Era 0.5
    return text, confidence
```

## 📝 Notas Importantes

### Rendimiento Esperado
- **CPU**: 10-15 FPS con YOLOv8n
- **GPU**: 30-60 FPS con YOLOv8n
- **Latencia**: ~100-150ms por frame

### Limitaciones Actuales (MVP)
- ✅ Exceso de velocidad: **Implementado** (básico)
- 🚧 Luz roja: **Pendiente** (requiere modelo de semáforos)
- 🚧 Invasión de carril: **Pendiente** (requiere detección de carriles)

### Mejoras Futuras
1. **Fine-tuning**: Entrenar YOLOv8 con dataset local (Perú)
2. **OCR optimizado**: Fine-tune EasyOCR para placas peruanas
3. **Tracking avanzado**: Implementar BoT-SORT o ByteTrack
4. **Velocidad precisa**: Optical Flow + Kalman Filter
5. **Multi-cámara**: Procesamiento paralelo de streams
6. **Detección de semáforos**: Agregar modelo traffic_lights.pt
7. **Segmentación de carriles**: Implementar lane detection

## 🐛 Troubleshooting

### Error: "Model not found"
```bash
# Descargar modelo manualmente
docker exec -it traffic-inference bash
mkdir -p /app/models
cd /app/models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### Error: "Failed to connect to Django"
```bash
# Verificar que Django esté corriendo
docker compose ps django

# Verificar conectividad
docker exec -it traffic-inference curl http://django:8000/health/
```

### OCR no detecta placas
- Verificar iluminación
- Acercar cámara al vehículo
- Ajustar umbral de confianza
- Verificar formato de placa (AAA-123)

### Velocidad incorrecta
- Se requiere calibración precisa
- Verificar historial de tracking (min 10 frames)
- Ajustar `meters_per_pixel`

## 📚 Referencias

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

**Estado actual**: ✅ Código completo | 🔄 Build en progreso | ⏳ Testing pendiente

