# Integración ML - YOLOv8 y OCR

## Descripción

Se ha integrado exitosamente YOLOv8 para detección de vehículos en tiempo real, EasyOCR para lectura de placas vehiculares, y registro automático de infracciones en la base de datos de Django.

## Componentes Implementados

### 1. Model Service (`inference-service/app/services/model_service.py`)

Servicio que gestiona los modelos de Machine Learning:

#### YOLOv8 - Detección de Vehículos
- **Modelo**: YOLOv8n (nano) para balance entre velocidad y precisión
- **Clases detectadas**: car, motorcycle, bus, truck
- **Configuración**:
  - Confidence threshold: 0.5 (configurable)
  - IOU threshold: 0.45
  - Ubicación modelo: `/app/models/yolov8n.pt`

#### EasyOCR - Detección de Placas
- **Idiomas**: Inglés (alphanumeric)
- **Formatos soportados** (Perú):
  - AAA-123 o AAA-1234 (3 letras + 3-4 números)
  - AB-1234 (2 letras + 4 números)
  - A12-345 (1 letra + 2 números + 3 números)
- **GPU**: Deshabilitado por defecto (configurable vía `OCR_GPU`)

#### Estimación de Velocidad
- Método: Tracking simple basado en desplazamiento de píxeles
- Requiere: Historial de detecciones (mínimo 10 frames)
- Calibración: 1 pixel ≈ 0.05 metros (ajustable con calibración de cámara)
- **Nota**: Para producción, implementar Optical Flow + Kalman Filter

### 2. Django API Service (`inference-service/app/services/django_api.py`)

Servicio para comunicación con el backend Django:

**Funcionalidades**:
- `create_infraction()`: Crea infracciones en la base de datos
- `get_or_create_vehicle()`: Obtiene o crea vehículos
- `get_device()`: Obtiene información del dispositivo
- `get_zone()`: Obtiene información de la zona
- `upload_evidence_to_minio()`: Sube evidencia a MinIO (placeholder)

### 3. WebSocket con Detección Real (`inference-service/app/api/websocket.py`)

Endpoint WebSocket actualizado con:

#### VehicleTracker
- Mantiene historial de detecciones por vehículo
- Máximo 30 frames de historia
- Limpieza automática de tracks antiguos

#### RealtimeDetector
**Flujo de procesamiento**:
1. Decodifica frame base64
2. Detecta vehículos con YOLOv8
3. Para cada vehículo:
   - Detecta placa con OCR (si habilitado)
   - Actualiza tracking
   - Estima velocidad (si hay suficiente historial)
   - Detecta infracciones
   - Registra en base de datos si aplica

**Tipos de infracciones detectadas**:
- ✅ **Exceso de velocidad**: Basado en estimación vs límite configurado
- 🚧 **Luz roja**: Placeholder (requiere detección de semáforos)
- 🚧 **Invasión de carril**: Placeholder (requiere detección de carriles)

### 4. Backend Django - Serializers y Views

#### InfractionCreateSerializer
- Acepta datos flexibles del servicio de inferencia
- Genera `infraction_code` automáticamente (formato: `INF-{TYPE}-{TIMESTAMP}`)
- Maneja defaults para device y zone si no se proporcionan

#### Endpoints API:
- `POST /api/infractions/`: Crear infracción (usado por servicio de inferencia)
- `GET /api/vehicles/?license_plate={plate}`: Buscar vehículo
- `POST /api/vehicles/`: Crear vehículo

## Configuración

### Variables de Entorno (inference-service)

```env
# ML Models
YOLO_MODEL_PATH=/app/models/yolov8n.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
YOLO_IOU_THRESHOLD=0.45
OCR_LANGUAGES=["en"]
OCR_GPU=false

# Django Backend API
DJANGO_API_URL=http://django:8000
DJANGO_API_TIMEOUT=30
```

### Dependencias Instaladas

```txt
ultralytics==8.0.230     # YOLOv8
easyocr==1.7.1          # OCR para placas
torch==2.2.2            # PyTorch
torchvision==0.17.2     # Visión computacional
opencv-python==4.9.0.80  # Procesamiento de imágenes
numpy==1.26.4           # Operaciones numéricas
```

## Flujo de Datos

```
1. [Frontend] Captura frame de cámara
   ↓
2. [Frontend] Envía frame base64 vía WebSocket
   ↓
3. [Inference Service] Recibe frame
   ↓
4. [YOLOv8] Detecta vehículos en frame
   ↓
5. [EasyOCR] Lee placas de cada vehículo
   ↓
6. [VehicleTracker] Actualiza historial de tracking
   ↓
7. [ModelService] Estima velocidad basada en tracking
   ↓
8. [RealtimeDetector] Detecta infracciones
   ↓
9. [DjangoAPI] Registra infracción en base de datos
   ├── Crea/obtiene vehículo
   ├── Obtiene device y zone
   └── Crea registro de infracción
   ↓
10. [WebSocket] Envía detecciones a frontend
    ↓
11. [Frontend] Muestra overlay con detecciones
```

## Modelo de Base de Datos

### Infraction
```python
{
    'id': UUID,
    'infraction_code': 'INF-SPE-20251102123045',  # Auto-generado
    'infraction_type': 'speed',  # speed, red_light, wrong_lane
    'severity': 'medium',  # low, medium, high, critical
    'vehicle': UUID,  # FK a Vehicle
    'device': UUID,  # FK a Device
    'zone': UUID,  # FK a Zone
    'license_plate_detected': 'ABC-123',
    'license_plate_confidence': 0.92,
    'detected_speed': 85.5,  # km/h
    'speed_limit': 60,  # km/h
    'snapshot_url': 's3://...',
    'evidence_metadata': {
        'detection_confidence': 0.87,
        'bbox': {'x': 100, 'y': 200, 'width': 150, 'height': 100},
        'infraction_data': {...}
    },
    'status': 'pending',  # pending, validated, rejected, etc.
    'detected_at': '2025-11-02T12:30:45Z',
    'created_at': '2025-11-02T12:30:46Z'
}
```

### Vehicle
```python
{
    'id': UUID,
    'license_plate': 'ABC-123',
    'vehicle_type': 'car',  # car, truck, bus, motorcycle
    'make': '',  # Marca (opcional)
    'model': '',  # Modelo (opcional)
    'year': null,
    'color': '',
    'owner_name': '',  # Se llenará con integración SUNARP
    'is_stolen': false,
    'is_wanted': false
}
```

## Uso

### Desde el Frontend

1. Navegar a "Monitoreo en Tiempo Real"
2. Seleccionar cámara (Web/Móvil/RTSP)
3. Configurar:
   - Límite de velocidad (km/h)
   - Tipos de infracciones a detectar
   - Umbral de confianza
   - Habilitar OCR y detección de velocidad
4. Iniciar detección
5. Ver detecciones en tiempo real con overlays
6. Las infracciones se registran automáticamente en la BD

### Verificar Infracciones Registradas

```bash
# Desde Django Admin
http://localhost:8000/admin/infractions/infraction/

# Desde API
curl http://localhost:8000/api/infractions/

# Filtrar por estado
curl http://localhost:8000/api/infractions/?status=pending

# Buscar por placa
curl http://localhost:8000/api/infractions/?search=ABC-123
```

## Rendimiento

### Configuración Actual (MVP)
- **Hardware**: CPU only
- **Modelo**: YOLOv8n (nano - más rápido)
- **FPS esperado**: 10-15 fps en CPU moderna
- **Latencia**: ~100-150ms por frame

### Optimización para Producción

1. **Usar GPU**:
   ```env
   INFERENCE_DEVICE=cuda
   GPU_DEVICE_ID=0
   OCR_GPU=true
   ```
   FPS esperado: 30-60 fps

2. **Modelo más preciso** (si tienes GPU potente):
   ```env
   YOLO_MODEL_PATH=/app/models/yolov8m.pt  # medium
   # o
   YOLO_MODEL_PATH=/app/models/yolov8l.pt  # large
   ```

3. **Batch Processing**:
   Procesar múltiples frames en batch para mejor throughput

4. **Model Optimization**:
   ```python
   # Exportar a TensorRT (NVIDIA GPU)
   model.export(format='engine')  # TensorRT
   
   # O ONNX (CPU optimizado)
   model.export(format='onnx')
   ```

## Limitaciones Actuales (MVP)

### ✅ Implementado
- Detección de vehículos (car, motorcycle, bus, truck)
- OCR de placas vehiculares (formatos Perú)
- Detección de exceso de velocidad (básica)
- Registro automático en base de datos
- Tracking simple de vehículos

### 🚧 Pendiente para Producción
1. **Luz roja**: Requiere modelo de detección de semáforos
2. **Invasión de carril**: Requiere detección de líneas de carril
3. **Velocidad precisa**: Implementar Optical Flow + Kalman Filter
4. **Calibración de cámara**: Para conversión pixel→metros precisa
5. **Upload de evidencias**: Integración completa con MinIO
6. **Modelo fine-tuned**: Entrenar con datos locales (Perú)
7. **OCR optimizado**: Fine-tuning para placas peruanas específicas
8. **Multi-cámara**: Procesamiento simultáneo de múltiples streams

## Mejoras Futuras

### Detección de Semáforos
```python
# Usar modelo adicional para detectar estado de semáforo
traffic_light_model = YOLO('traffic_lights.pt')
light_state = traffic_light_model.predict(frame)  # red, yellow, green
```

### Detección de Carriles
```python
# Usar modelos de segmentación de carriles
from ultralytics import YOLO
lane_model = YOLO('lane_detection.pt')
lanes = lane_model.predict(frame)
```

### Tracking Avanzado
```python
# Usar BoT-SORT o ByteTrack para tracking robusto
from ultralytics.trackers import BOTSORT
tracker = BOTSORT()
tracked_objects = tracker.update(detections)
```

### Fine-tuning del Modelo
```python
# Entrenar con dataset local
model = YOLO('yolov8n.pt')
model.train(
    data='peru_vehicles.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)
```

## Troubleshooting

### Modelo YOLO no se descarga
```bash
# Descargar manualmente
docker exec -it traffic-inference bash
cd /app/models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### OCR no detecta placas
- Verificar iluminación de la cámara
- Ajustar umbral de confianza
- Verificar formato de placa (debe ser AAA-123)
- Probar con imagen más cercana del vehículo

### Velocidad estimada incorrecta
- Se requiere calibración de cámara
- Verificar que el vehículo tenga suficiente historial (10+ frames)
- Ajustar `meters_per_pixel` en calibration_data

### Infracciones no se registran
- Verificar logs: `docker compose logs inference`
- Verificar conectividad con Django: `curl http://django:8000/health/`
- Verificar que device y zone existan en la BD
- Verificar formato de placa detectada

## Monitoreo

### Logs del Servicio
```bash
# Ver logs en tiempo real
docker compose logs -f inference

# Buscar errores
docker compose logs inference | grep ERROR

# Ver estadísticas de detección
docker compose logs inference | grep "Infraction registered"
```

### Métricas
- Detecciones por segundo
- Precisión de OCR (confidence promedio)
- Infracciones registradas por hora
- Tasa de false positives

## Soporte

Para reportar issues o sugerencias sobre la integración ML:
- Logs del servicio de inferencia
- Screenshot del error
- Configuración utilizada
- Tipo de cámara y condiciones de iluminación

