# Diagrama de Flujo: Detección con Bounding Boxes

## Flujo Completo del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SISTEMA DE DETECCIÓN                             │
└─────────────────────────────────────────────────────────────────────────┘

1. INICIO DE TRANSMISIÓN
   ━━━━━━━━━━━━━━━━━━━━

   Frontend                     Backend Django              Inference Service
   ────────                     ──────────────              ─────────────────
      │                                │                            │
      │  GET /api/devices/{id}         │                            │
      │───────────────────────────────>│                            │
      │                                │                            │
      │  { rtsp_url, name, config }    │                            │
      │<───────────────────────────────│                            │
      │                                │                            │
      │                                │                            │
      │  WebSocket Connect:            │                            │
      │  ws://localhost:8001/stream/ws/camera/{id}?camera_url=...  │
      │────────────────────────────────────────────────────────────>│
      │                                │                            │
      │  WebSocket Accepted            │                            │
      │<────────────────────────────────────────────────────────────│
      │                                │                            │


2. CONFIGURACIÓN INICIAL
   ━━━━━━━━━━━━━━━━━━━━━

   Frontend                                          Inference Service
   ────────                                          ─────────────────
      │                                                     │
      │  { type: "config",                                 │
      │    config: {                                       │
      │      confidence_threshold: 0.7,                    │
      │      enable_ocr: true,                             │
      │      enable_speed: true,                           │
      │      infractions: ["speeding", "red_light"],       │
      │      speed_limit: 60                               │
      │    }                                               │
      │  }                                                 │
      │────────────────────────────────────────────────────>│
      │                                                     │
      │                                                     │ Inicializa YOLOv8
      │                                                     │ Carga modelo OCR
      │                                                     │ Conecta a cámara RTSP
      │                                                     │


3. PROCESAMIENTO DE FRAMES (LOOP CONTINUO)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                 Inference Service
                 ─────────────────
                        │
   ┌────────────────────┴────────────────────┐
   │ CameraStreamManager                     │
   │                                         │
   │  1. Captura frame de RTSP               │
   │     cap.read() → frame (np.ndarray)     │
   │                                         │
   │  2. Codifica a base64                   │
   │     cv2.imencode() → base64             │
   │                                         │
   │  3. Detección con YOLOv8                │
   │     model_service.detect_vehicles()     │
   │     ↓                                   │
   │     [                                   │
   │       {                                 │
   │         bbox: {x, y, width, height},    │
   │         confidence: 0.95,               │
   │         vehicle_type: "car"             │
   │       }                                 │
   │     ]                                   │
   │                                         │
   │  4. OCR en placas                       │
   │     model_service.detect_license_plate()│
   │     ↓                                   │
   │     { plate: "ABC123", conf: 0.88 }    │
   │                                         │
   │  5. Estimación de velocidad             │
   │     model_service.estimate_speed()      │
   │     ↓                                   │
   │     { speed: 75.5 km/h }               │
   │                                         │
   │  6. Detección de infracciones           │
   │     if speed > speed_limit:             │
   │       register_infraction()             │
   │                                         │
   │  7. Envía resultado                     │
   └─────────────────┬───────────────────────┘
                     │
                     │  WebSocket Message:
                     │  {
                     │    type: "frame",
                     │    frame: "base64...",
                     │    frame_number: 1234,
                     │    detections: [...]
                     │  }
                     ▼
              Frontend Canvas
              ───────────────


4. RENDERIZADO EN FRONTEND
   ━━━━━━━━━━━━━━━━━━━━━━━━

   VideoPlayerWithDetection Component
   ──────────────────────────────────

   ┌─────────────────────────────────────┐
   │  WebSocket.onmessage                │
   │                                     │
   │  1. Recibe mensaje                  │
   │     { frame, detections }           │
   │                                     │
   │  2. Crea imagen desde base64        │
   │     img.src = "data:image/jpeg..."  │
   │                                     │
   │  3. Dibuja en canvas                │
   │     ctx.drawImage(img, 0, 0)        │
   │                                     │
   │  4. Dibuja bounding boxes           │
   │     for detection in detections:    │
   │       ctx.strokeRect(bbox)          │
   │       ctx.fillText(label)           │
   │                                     │
   │  5. Actualiza stats                 │
   │     - FPS counter                   │
   │     - Detection count               │
   │     - Connection status             │
   └─────────────────────────────────────┘


5. VISUALIZACIÓN FINAL
   ━━━━━━━━━━━━━━━━━━━━

   ┌────────────────────────────────────────────────┐
   │ 🟢 Conectado | FPS: 30 | Detecciones: 3       │ ← Stats Overlay
   ├────────────────────────────────────────────────┤
   │                                                │
   │    ┌──────────────────────┐                   │
   │    │ car | 95% | ABC123   │  ← Label          │
   │    └──────────────────────┘                   │
   │    ┏━━━━━━━━━━━━━━━━━━━━━━┓                   │
   │    ┃                      ┃                   │
   │    ┃   [Vehículo 1]       ┃  ← Bounding Box   │
   │    ┃                      ┃     (Verde)       │
   │    ┗━━━━━━━━━━━━━━━━━━━━━━┛                   │
   │                                                │
   │         ┏━━━━━━━━━━━━┓                        │
   │         ┃            ┃                        │
   │         ┃ [Vehículo] ┃                        │
   │         ┗━━━━━━━━━━━━┛                        │
   │                                                │
   │                        ┏━━━━━━━━━━┓           │
   │                        ┃ [Vehíc.] ┃           │
   │                        ┗━━━━━━━━━━┛           │
   │                                                │
   ├────────────────────────────────────────────────┤
   │ Cámara Principal - Zona Centro                │ ← Device Name
   └────────────────────────────────────────────────┘
                         │
                         │ [⛶] Fullscreen
                         └──────────────────


6. REGISTRO DE INFRACCIONES
   ━━━━━━━━━━━━━━━━━━━━━━━━━

   Inference Service                  Backend Django
   ─────────────────                  ──────────────
         │                                  │
         │ Si se detecta infracción:        │
         │ - Velocidad > límite              │
         │ - Semáforo en rojo               │
         │ - Invasión de carril             │
         │                                  │
         │ POST /api/infractions/           │
         │ {                                │
         │   license_plate: "ABC123",       │
         │   infraction_type: "speeding",   │
         │   detected_speed: 85.3,          │
         │   speed_limit: 60,               │
         │   confidence: 0.95,              │
         │   image: "base64...",            │
         │   device: "camera-id"            │
         │ }                                │
         │─────────────────────────────────>│
         │                                  │
         │                                  │ Guarda en DB
         │                                  │ Genera notificación
         │                                  │ Registra evento
         │                                  │
         │ { id: 123, status: "created" }   │
         │<─────────────────────────────────│
         │                                  │


7. PERFORMANCE Y OPTIMIZACIÓN
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Configuración                    Efecto
   ───────────────────────────────────────────────────────
   process_interval = 1             Procesa cada frame (30 FPS)
   process_interval = 2             Procesa cada 2 frames (15 FPS)
   process_interval = 3             Procesa cada 3 frames (10 FPS)
   
   confidence_threshold = 0.5       Más detecciones (más falsos positivos)
   confidence_threshold = 0.7       Balance (recomendado)
   confidence_threshold = 0.9       Menos detecciones (más precisas)
   
   YOLOv8n                          Rápido, menos preciso
   YOLOv8s                          Balance
   YOLOv8m/l                        Lento, más preciso


8. MANEJO DE ERRORES
   ━━━━━━━━━━━━━━━━━━

   Error                        Acción
   ─────────────────────────────────────────────────────
   Camera no disponible         → Reintento cada 1s
   WebSocket desconectado       → Cierra stream
   Frame decode error           → Salta frame
   YOLOv8 error                 → Log error, continúa
   OCR timeout                  → Continúa sin placa
   Django API down              → Log warning, no registra infracción
```

## Comparación: Antes vs Después

### ANTES (Sin bounding boxes)
```
Frontend: [Imagen de cámara sin procesar]
- No hay indicación de detecciones
- No hay información de vehículos
- No hay visualización de infracciones
```

### DESPUÉS (Con bounding boxes)
```
Frontend: [Imagen con recuadros verdes]
┏━━━━━━━━━━━━━━━━┓
┃ car | 95.2%    ┃
┃ ABC123         ┃ ← Placa detectada
┃ 75.5 km/h      ┃ ← Velocidad estimada
┗━━━━━━━━━━━━━━━━┛
↓
Usuario ve claramente:
✓ Qué vehículos fueron detectados
✓ Nivel de confianza de cada detección
✓ Placas leídas por OCR
✓ Velocidades estimadas
✓ Infracciones en tiempo real
```

## Tecnologías Utilizadas

```
┌─────────────┬──────────────────────────────────────┐
│ Frontend    │ React + TypeScript                   │
│             │ Canvas API (dibujo de bounding boxes)│
│             │ WebSocket API (conexión en tiempo real)│
├─────────────┼──────────────────────────────────────┤
│ Backend     │ FastAPI + Python 3.11+               │
│             │ OpenCV (captura y procesamiento)     │
│             │ YOLOv8 (detección de objetos)        │
│             │ EasyOCR (lectura de placas)          │
├─────────────┼──────────────────────────────────────┤
│ Comunicación│ WebSocket (bidireccional)            │
│             │ JSON (formato de mensajes)           │
│             │ Base64 (codificación de imágenes)    │
├─────────────┼──────────────────────────────────────┤
│ Database    │ PostgreSQL + Django ORM              │
│             │ Almacena infracciones detectadas     │
└─────────────┴──────────────────────────────────────┘
```
