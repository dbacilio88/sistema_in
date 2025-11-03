# Guía: Detección con Webcam Local

## Nueva Funcionalidad Agregada

Se ha agregado una nueva sección en el **Monitoreo en Tiempo Real** que permite usar la **webcam local** de tu computadora para realizar detecciones de vehículos en tiempo real.

## Ubicación

```
Dashboard → Monitoreo en Tiempo Real → Sección "Webcam Local"
```

## Características

### 🎥 Webcam Local
- **Captura video** directamente desde tu cámara web
- **Procesamiento en tiempo real** con YOLOv8
- **Detección de vehículos**: autos, camiones, buses, motos, bicicletas
- **OCR de placas** (si son visibles)
- **Bounding boxes de colores** según tipo de vehículo
- **Estadísticas en vivo**: FPS y contador de detecciones

### 🎨 Colores por Tipo de Vehículo

| Tipo | Color | Código |
|------|-------|--------|
| Auto (car) | Verde | `#00ff00` |
| Camión (truck) | Naranja | `#ff9800` |
| Bus | Azul | `#2196f3` |
| Moto (motorcycle) | Morado | `#9c27b0` |
| Bicicleta (bicycle) | Amarillo | `#ffeb3b` |
| Persona (person) | Naranja oscuro | `#ff5722` |
| Infracción | Rojo | `#ff0000` |

### 📊 Información Mostrada

Cada detección muestra:
- **Tipo de vehículo**
- **Nivel de confianza** (porcentaje)
- **Placa vehicular** (si es legible)
- **Tipo de infracción** (si aplica)

## Cómo Usar

### 1. Acceder a la Sección

```
http://localhost:3000/realtime
```

Verás dos secciones principales:
- **Webcam Local** (nueva) - Arriba
- **Cámaras del Sistema** - Abajo

### 2. Iniciar Webcam

1. En la sección "Webcam Local", haz click en **"Iniciar Webcam"**
2. El navegador te pedirá permiso para acceder a la cámara
3. Haz click en **"Permitir"**
4. La webcam comenzará a transmitir con detecciones en tiempo real

### 3. Visualizar Detecciones

Una vez iniciada, verás:
- **Video en vivo** de tu webcam
- **Recuadros de colores** alrededor de objetos detectados
- **Etiquetas** con información de cada detección
- **Stats overlay** (esquina superior izquierda):
  - Estado de conexión
  - FPS actual
  - Número de detecciones
- **Leyenda de colores** (esquina inferior izquierda)

### 4. Detener Webcam

- Haz click en el botón rojo **"Detener"** (esquina inferior derecha)
- O simplemente navega a otra página

## Requisitos

### Hardware
- **Webcam** integrada o externa
- **Conexión estable** a internet
- **CPU/GPU** con capacidad para procesamiento de video

### Software
- **Navegador moderno** con soporte para WebRTC:
  - Chrome 53+
  - Firefox 36+
  - Safari 11+
  - Edge 79+
- **Permisos de cámara** habilitados en el navegador

### Servicios
- **Inference Service** corriendo en `localhost:8001`
- **Backend Django** corriendo en `localhost:8000`

## Diferencias: Webcam Local vs Cámaras del Sistema

| Característica | Webcam Local | Cámaras del Sistema |
|----------------|--------------|---------------------|
| Fuente | Navegador web (getUserMedia API) | RTSP/IP Cameras |
| Procesamiento | Cliente → Servidor | Servidor directo |
| Configuración | No requiere | Requiere RTSP URL |
| Movilidad | Portátil | Fija |
| Calidad | Depende de la webcam | Generalmente HD/4K |
| Latencia | Media (encoding/decoding) | Baja |
| Uso ideal | Testing, demos, desarrollo | Producción, monitoreo 24/7 |

## Arquitectura Técnica

```
┌──────────────┐
│  Navegador   │
│              │
│  Webcam API  │  navigator.mediaDevices.getUserMedia()
│     ↓        │
│  Video       │  Captura frames a 30 FPS
│     ↓        │
│  Canvas      │  Convierte a JPEG base64
│     ↓        │
│  WebSocket   │  Envía al servidor
└──────┬───────┘
       │
       │ ws://localhost:8001/ws/inference
       ↓
┌──────────────────┐
│ Inference Service│
│                  │
│  • Recibe frame  │
│  • YOLOv8 detect │
│  • OCR placas    │
│  • Retorna JSON  │
└──────┬───────────┘
       │
       │ { detections: [...] }
       ↓
┌──────────────┐
│  Navegador   │
│              │
│  Canvas      │  Dibuja bounding boxes
│     ↓        │
│  Usuario     │  Ve detecciones en vivo
└──────────────┘
```

## Flujo de Datos

1. **Captura**: `navigator.mediaDevices.getUserMedia()` captura video
2. **Frame extraction**: Canvas extrae frame actual como imagen
3. **Encoding**: Frame se convierte a JPEG base64
4. **Transmisión**: WebSocket envía frame al servidor
5. **Detección**: YOLOv8 procesa y detecta objetos
6. **Respuesta**: Servidor retorna coordenadas de detecciones
7. **Renderizado**: Canvas dibuja bounding boxes sobre el video

## Configuración Avanzada

### Ajustar Calidad de Video

Edita `LocalWebcamDetection.tsx`:

```typescript
const stream = await navigator.mediaDevices.getUserMedia({
  video: {
    width: { ideal: 1920 },  // Cambiar resolución
    height: { ideal: 1080 },
    frameRate: { ideal: 30 }  // Cambiar FPS
  }
});
```

### Ajustar Umbral de Confianza

```typescript
config: {
  confidence_threshold: 0.7,  // 0.0 - 1.0 (más bajo = más detecciones)
  enable_ocr: true,           // Activar/desactivar OCR
  enable_speed: false,        // No aplica para webcam
}
```

### Procesar Cada N Frames

Para mejorar performance, procesa solo cada N frames:

```typescript
// En sendFrameToInference(), agregar:
if (frameCount % 2 === 0) {  // Procesa cada 2 frames (15 FPS)
  // Send to inference
}
```

## Casos de Uso

### 1. Testing y Desarrollo
- Prueba el sistema sin necesidad de cámaras RTSP
- Desarrolla y depura funcionalidades de detección
- Demo rápido del sistema

### 2. Monitoreo Temporal
- Vigila un área específica temporalmente
- Portátil - lleva tu laptop donde necesites
- Sin instalación de hardware

### 3. Capacitación
- Entrena personal en el uso del sistema
- Muestra cómo funciona la detección
- Valida configuraciones

### 4. Detección de Objetos en Escritorio
- Detecta objetos cerca de tu computadora
- Útil para inventario, conteo, etc.

## Limitaciones

### ❌ No Recomendado Para:
- Monitoreo 24/7 de producción
- Grandes distancias (calidad de webcam limitada)
- Múltiples ángulos simultáneos
- Condiciones climáticas adversas

### ⚠️ Consideraciones:
- **Calidad**: Depende de la webcam
- **Iluminación**: Requiere buena luz ambiental
- **Distancia**: Objetos deben estar relativamente cerca
- **Ángulo**: Mejor frontal o semi-lateral
- **Performance**: Consume CPU/GPU local

## Troubleshooting

### Error: "Permiso de cámara denegado"
**Solución**: 
1. Click en el ícono de candado en la barra de direcciones
2. Permitir acceso a cámara
3. Recarga la página

### Error: "No se pudo conectar con el servicio"
**Solución**:
1. Verifica que Inference Service esté corriendo: `http://localhost:8001/docs`
2. Revisa logs del servidor
3. Verifica que no haya firewall bloqueando WebSocket

### FPS muy bajo (< 10)
**Solución**:
1. Reduce resolución de webcam
2. Aumenta `process_interval` (procesa cada 2-3 frames)
3. Reduce `confidence_threshold` para menos procesamiento
4. Cierra otras aplicaciones pesadas

### Detecciones imprecisas
**Solución**:
1. Mejora iluminación del área
2. Acerca objetos a la cámara
3. Usa webcam de mejor calidad
4. Ajusta `confidence_threshold` más alto (0.8-0.9)

### Video congelado
**Solución**:
1. Detén y reinicia webcam
2. Recarga la página
3. Verifica conexión a internet
4. Revisa consola del navegador (F12) para errores

## Mejoras Futuras

### Planeadas:
- [ ] Selección de múltiples webcams
- [ ] Grabación de video con detecciones
- [ ] Captura de screenshots de infracciones
- [ ] Configuración de áreas de interés (ROI)
- [ ] Filtros y ajustes de imagen en tiempo real
- [ ] Estadísticas históricas de detecciones
- [ ] Exportar datos de detecciones (CSV/JSON)

## Soporte

Si encuentras problemas:
1. Revisa la consola del navegador (F12)
2. Verifica logs del Inference Service
3. Consulta la documentación técnica en `/docs`
4. Reporta issues en el repositorio

---

**Última actualización**: Noviembre 2, 2025
**Versión**: 1.0.0
