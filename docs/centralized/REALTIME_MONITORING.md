# Módulo de Monitoreo en Tiempo Real

## Descripción

Este módulo permite la detección en tiempo real de vehículos e infracciones de tránsito utilizando diferentes fuentes de video:
- Cámara web local
- Dispositivo móvil (cámara)
- Streams RTSP de cámaras IP

## Características

### 🎥 Fuentes de Video
- **Cámara Web Local**: Acceso directo a la cámara web del computador
- **Dispositivo Móvil**: Acceso a la cámara del dispositivo móvil
- **RTSP Stream**: Conexión a cámaras IP mediante protocolo RTSP

### 🚗 Detección de Vehículos
- Identificación de vehículos en tiempo real con recuadros verdes
- Confianza de detección mostrada en porcentaje
- Detección de placas vehiculares (OCR)

### ⚠️ Detección de Infracciones
Los siguientes tipos de infracciones son detectados con recuadros de colores específicos:

- **Exceso de Velocidad** (Recuadro Naranja)
  - Detecta vehículos que superan el límite de velocidad configurado
  - Muestra velocidad detectada vs límite permitido
  
- **Pasarse la Luz Roja** (Recuadro Rojo)
  - Identifica vehículos que no respetan semáforos en rojo
  
- **Invasión de Carril** (Recuadro Amarillo)
  - Detecta vehículos que invaden carriles no permitidos

### ⚙️ Configuración
- **Límite de Velocidad**: Configurable por el usuario (20-120 km/h)
- **Umbral de Confianza**: Ajustable para filtrar detecciones (50%-95%)
- **Detección de Placas (OCR)**: Activable/desactivable
- **Detección de Velocidad**: Activable/desactivable

### 📊 Panel de Monitoreo
- Visualización del stream de video en tiempo real
- Overlay de detecciones con información detallada
- Lista de detecciones recientes con timestamps
- Métricas de rendimiento (FPS, número de detecciones)
- Estado de conexión en tiempo real

## Arquitectura Técnica

### Frontend (`RealtimeMonitor.tsx`)
- **Framework**: React + Next.js 14 + TypeScript
- **Video API**: WebRTC (getUserMedia) para acceso a cámaras locales
- **WebSocket**: Comunicación bidireccional con el backend para inferencia
- **Canvas API**: Renderizado de detecciones sobre el video

### Backend (Inference Service)
- **Framework**: FastAPI + WebSockets
- **Ubicación**: `inference-service/app/api/websocket.py`
- **Endpoint**: `ws://localhost:8001/api/v1/ws/inference`
- **Procesamiento**: OpenCV + NumPy para análisis de frames

### Flujo de Datos

```
[Cámara] → [Frontend: Video Stream] → [Canvas Capture] → [Base64 Frame]
    ↓
[WebSocket Send] → [Backend: Inference Service] → [ML Models]
    ↓
[Detection Results] ← [WebSocket Receive] ← [Backend Response]
    ↓
[Canvas Overlay] → [Visual Feedback]
```

## Uso

### 1. Acceder al Módulo
- Inicia sesión en el dashboard
- En el menú lateral, selecciona "Monitoreo en Tiempo Real"

### 2. Seleccionar Fuente de Video
- Escoge entre: Cámara Web Local, Dispositivo Móvil o RTSP
- Para RTSP, ingresa la URL del stream (ej: `rtsp://192.168.1.10:554/stream`)

### 3. Configurar Detección
- Ajusta el límite de velocidad según la zona
- Selecciona los tipos de infracciones a monitorear
- Configura el umbral de confianza
- Activa/desactiva OCR y detección de velocidad

### 4. Iniciar Monitoreo
- Clic en "Iniciar Detección"
- El sistema solicitará permisos de acceso a la cámara (primera vez)
- El video comenzará a procesarse en tiempo real

### 5. Interpretar Resultados
- **Recuadros Verdes**: Vehículos detectados sin infracciones
- **Recuadros Naranjas**: Exceso de velocidad
- **Recuadros Rojos**: Luz roja
- **Recuadros Amarillos**: Invasión de carril
- Cada detección muestra: tipo, confianza, placa (si se detecta), velocidad (si aplica)

## Permisos de Navegador

### Cámara Web/Móvil
El navegador solicitará permiso para acceder a la cámara. Asegúrate de:
- Permitir acceso a la cámara en el navegador
- Verificar que no haya otras aplicaciones usando la cámara
- En HTTPS, los permisos son más estrictos

### Recomendaciones
- Usar Chrome/Edge para mejor compatibilidad
- Conexión HTTPS en producción
- Buena iluminación para mejor detección
- Cámara estable (evitar movimientos bruscos)

## Integración con ML

### Estado Actual (MVP)
El módulo actualmente usa **detección simulada** para el MVP con:
- Generación aleatoria de detecciones para pruebas
- Simulación de confianza, posiciones y tipos de infracciones
- Datos de prueba para placas y velocidades

### Roadmap de Integración
Para integrar modelos de ML reales:

1. **Detección de Vehículos**: YOLOv8 o YOLO11
2. **OCR de Placas**: EasyOCR o PaddleOCR
3. **Detección de Velocidad**: Optical Flow + Kalman Filter
4. **Clasificación de Infracciones**: Modelos personalizados entrenados

Ver: `inference-service/app/api/websocket.py` - método `_simulate_detection`

## Configuración Técnica

### Variables de Entorno

```env
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ML_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_WS_INFERENCE_URL=ws://localhost:8001

# Inference Service
INFERENCE_DEVICE=cpu  # o 'cuda' para GPU
GPU_DEVICE_ID=0
```

### Docker Compose

Los servicios necesarios están configurados en `docker-compose.yml`:
- `frontend`: Puerto 3002 → 3000
- `inference`: Puerto 8001

```bash
# Reconstruir y reiniciar servicios
docker compose build frontend inference
docker compose up -d frontend inference

# Ver logs
docker compose logs -f inference
docker compose logs -f frontend
```

## Troubleshooting

### La cámara no se detecta
- Verificar permisos del navegador
- Cerrar otras aplicaciones que usen la cámara
- Reiniciar el navegador
- Probar en modo incógnito

### WebSocket no conecta
- Verificar que el servicio de inferencia esté corriendo: `docker compose ps inference`
- Ver logs del servicio: `docker compose logs inference`
- Verificar firewall/antivirus no bloquee el puerto 8001

### Bajo rendimiento (FPS)
- Reducir resolución del video
- Aumentar umbral de confianza
- Desactivar OCR si no es necesario
- Usar GPU si está disponible (`INFERENCE_DEVICE=cuda`)

### No se detectan infracciones
- Verificar tipos de infracciones seleccionados
- Ajustar umbral de confianza (menor valor = más detecciones)
- Asegurar buena iluminación y ángulo de cámara
- Nota: En MVP usa detección simulada, las detecciones son aleatorias

## Próximos Pasos

1. **Integración de Modelos Reales**
   - [ ] YOLOv8 para detección de vehículos
   - [ ] Modelo de OCR para placas vehiculares
   - [ ] Sistema de tracking para cálculo de velocidad
   - [ ] Clasificadores de infracciones

2. **Mejoras de UX**
   - [ ] Grabación de sesiones
   - [ ] Exportación de reportes
   - [ ] Alertas en tiempo real
   - [ ] Múltiples cámaras simultáneas

3. **Optimizaciones**
   - [ ] Procesamiento en GPU
   - [ ] Compresión de frames
   - [ ] Caché de resultados
   - [ ] Load balancing para múltiples streams

## Documentación Adicional

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [WebRTC getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [OpenCV Python](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

## Soporte

Para reportar problemas o sugerencias, contactar al equipo de desarrollo.
