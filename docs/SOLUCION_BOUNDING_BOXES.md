# Solución: Recuadros de Detección de Infracciones

## Problema
Los recuadros de detección (bounding boxes) no se generaban al hacer pruebas en el sistema de monitoreo en tiempo real.

## Análisis del Problema

El sistema tenía los siguientes componentes trabajando, pero desconectados:

1. **Inference Service** - Procesaba frames y detectaba vehículos con YOLOv8, pero solo retornaba coordenadas JSON sin dibujar los recuadros
2. **Frontend** - Mostraba video directo desde la cámara sin procesar las detecciones
3. **WebSocket** - Existía pero esperaba que el cliente enviara frames, no los proporcionaba

### Arquitectura Anterior
```
Cámara → Django API → Frontend (video sin procesar)
                ↓
        Inference Service (no conectado)
```

## Solución Implementada

### 1. Nuevo Endpoint de Streaming (`stream.py`)

Creé un nuevo endpoint WebSocket que:
- Se conecta directamente a la cámara vía RTSP
- Captura frames en tiempo real
- Procesa cada frame con YOLOv8 para detectar vehículos
- Envía frames + detecciones al frontend

**Ubicación**: `inference-service/app/api/stream.py`

**Endpoint**: `ws://localhost:8001/stream/ws/camera/{device_id}`

```python
@router.websocket("/ws/camera/{device_id}")
async def websocket_camera_stream(websocket, device_id, camera_url):
    # Conecta a la cámara RTSP
    cap = cv2.VideoCapture(camera_url)
    
    # Lee frames continuamente
    while True:
        ret, frame = cap.read()
        
        # Procesa con YOLOv8
        result = await detector.process_frame(frame, config)
        
        # Envía frame + detecciones al frontend
        await websocket.send_json({
            "frame": frame_base64,
            "detections": result["detections"]
        })
```

### 2. Componente Frontend con Canvas (`VideoPlayerWithDetection.tsx`)

Creé un nuevo componente React que:
- Se conecta al WebSocket de streaming
- Recibe frames con detecciones
- Dibuja los recuadros en un canvas HTML5
- Muestra información de detección (tipo de vehículo, confianza, placa, velocidad)

**Ubicación**: `frontend-dashboard/src/components/VideoPlayerWithDetection.tsx`

**Características**:
- Canvas HTML5 para dibujar bounding boxes
- Recuadros verdes con información superpuesta
- Stats overlay (FPS, número de detecciones, estado de conexión)
- Manejo de errores y reconexión automática

```typescript
const drawDetections = (ctx, detections) => {
  detections.forEach((detection) => {
    // Dibuja rectángulo verde
    ctx.strokeStyle = '#00ff00';
    ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);
    
    // Dibuja etiqueta con info
    const label = `${vehicle_type} | ${confidence}% | ${license_plate}`;
    ctx.fillText(label, bbox.x, bbox.y - 10);
  });
};
```

### 3. Actualización del Componente de Monitoreo

Actualicé `RealtimeMonitorView.tsx` para usar el nuevo componente:

```typescript
import { VideoPlayerWithDetection } from './VideoPlayerWithDetection';

// Reemplazó VideoPlayer con VideoPlayerWithDetection
<VideoPlayerWithDetection
  deviceId={device.id}
  deviceName={device.name}
  onError={handleError}
/>
```

### 4. Registro del Nuevo Router

Activé el router de streaming en la API:

**Archivo**: `inference-service/app/api/__init__.py`

```python
from .stream import router as stream_router
router.include_router(stream_router, prefix="/stream", tags=["stream"])
```

## Nueva Arquitectura

```
┌─────────┐        RTSP         ┌──────────────────┐
│ Cámara  │──────────────────────►│ Inference        │
└─────────┘                       │ Service          │
                                  │                  │
                                  │ • Captura frames │
                                  │ • YOLOv8 detect  │
                                  │ • OCR placas     │
                                  └────────┬─────────┘
                                           │ WebSocket
                                           │ {frame, detections}
                                           ▼
                                  ┌─────────────────┐
                                  │ Frontend        │
                                  │ Canvas Drawing  │
                                  │                 │
                                  │ • Dibuja bbox   │
                                  │ • Muestra info  │
                                  └─────────────────┘
```

## Formato de Datos

### Mensaje WebSocket (Backend → Frontend)

```json
{
  "type": "frame",
  "frame": "base64_encoded_image_data...",
  "frame_number": 1234,
  "timestamp": "2024-01-15T10:30:45.123456",
  "detections": [
    {
      "id": "1234-0",
      "type": "vehicle",
      "vehicle_type": "car",
      "confidence": 0.95,
      "bbox": {
        "x": 120,
        "y": 200,
        "width": 150,
        "height": 100
      },
      "license_plate": "ABC123",
      "license_confidence": 0.88,
      "speed": 75.5
    }
  ]
}
```

## Configuración

### Variables de Entorno

**Frontend** (`frontend-dashboard/.env`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_INFERENCE_WS=ws://localhost:8001
```

**Inference Service** (`inference-service/.env`):
```bash
MODEL_PATH=./models/yolov8n.pt
CONFIDENCE_THRESHOLD=0.7
```

## Pruebas

### 1. Verificar Inference Service
```bash
cd inference-service
python -m uvicorn app.main:app --reload --port 8001
```

### 2. Verificar Frontend
```bash
cd frontend-dashboard
npm run dev
```

### 3. Abrir Dashboard
```
http://localhost:3000/realtime
```

### 4. Seleccionar Cámara
1. Seleccionar una cámara de la lista
2. Click en "Iniciar Transmisión"
3. Verificar que aparecen recuadros verdes alrededor de los vehículos detectados

## Componentes Afectados

### Archivos Nuevos
- `inference-service/app/api/stream.py` - Nuevo endpoint de streaming
- `frontend-dashboard/src/components/VideoPlayerWithDetection.tsx` - Componente con canvas

### Archivos Modificados
- `inference-service/app/api/__init__.py` - Registro del router
- `inference-service/app/api/websocket.py` - Actualizado para retornar frames
- `frontend-dashboard/src/components/RealtimeMonitorView.tsx` - Usa nuevo componente

## Características Visuales

### Bounding Boxes
- **Color**: Verde (`#00ff00`)
- **Grosor**: 3px
- **Contenido**: Tipo de vehículo, confianza, placa, velocidad

### Overlay de Información
- **Top-left**: Estado de conexión, FPS, número de detecciones
- **Top-right**: Botón de pantalla completa
- **Bottom**: Nombre del dispositivo

## Próximas Mejoras

1. **Configuración dinámica** - Permitir ajustar umbrales desde UI
2. **Grabación** - Guardar clips de video con detecciones
3. **Zoom** - Hacer zoom en detecciones específicas
4. **Multi-cámara sincronizada** - Vista de múltiples cámaras con detecciones
5. **Alertas visuales** - Resaltar infracciones en rojo
6. **Histórico** - Reproducir detecciones pasadas

## Resolución de Problemas

### Los recuadros no aparecen
1. Verificar que el Inference Service está corriendo (`localhost:8001`)
2. Verificar logs del navegador (F12 → Console)
3. Verificar que la cámara tiene `rtsp_url` configurado en Django

### Error de conexión WebSocket
1. Verificar URL del WebSocket en el componente
2. Verificar que no hay CORS blocking
3. Verificar firewall/puertos

### Baja performance/FPS bajo
1. Ajustar `process_interval` en la configuración (procesar cada N frames)
2. Reducir resolución de la cámara
3. Usar modelo YOLOv8n (nano) en lugar de YOLOv8m/l

## Conclusión

La solución implementa un pipeline completo de detección en tiempo real con visualización de bounding boxes. El sistema ahora:

✅ Captura frames desde cámaras RTSP
✅ Procesa con YOLOv8 para detectar vehículos
✅ Dibuja recuadros de detección en tiempo real
✅ Muestra información de detecciones (tipo, confianza, placa, velocidad)
✅ Registra infracciones en la base de datos
✅ Proporciona feedback visual al usuario

El usuario ahora puede ver claramente las detecciones con recuadros verdes alrededor de cada vehículo detectado.
