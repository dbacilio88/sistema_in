# 🎬 Guía de Detección con Archivos de Video

## 📋 Resumen

El sistema ahora soporta detección de infracciones utilizando archivos de video pregrabados, además de la webcam en tiempo real. Esto permite:

- Probar el sistema con videos de ejemplo
- Depurar detecciones con escenarios controlados
- Demostrar el sistema sin necesidad de cámara
- Entrenar y ajustar parámetros con videos de referencia

---

## 🚀 Características

### ✅ Funcionalidades Implementadas

1. **Selección de Fuente**:
   - 📷 Webcam en tiempo real
   - 🎬 Archivo de video pregrabado

2. **Formatos Soportados**:
   - MP4 (H.264, H.265)
   - AVI
   - MOV
   - WebM
   - MKV

3. **Reproducción**:
   - Loop automático (video se repite)
   - Sin audio (muted)
   - Compatible con dispositivos móviles (playsInline)

4. **Detecciones Disponibles**:
   - ✅ Velocidad (simulada)
   - ✅ Semáforo en rojo
   - ✅ Invasión de carril
   - ✅ Detección de placas (OCR)

---

## 📖 Cómo Usar

### 1. Seleccionar Modo de Video

**En el Dashboard de Detección:**

1. Antes de iniciar la detección
2. En la sección "📹 Fuente de Video"
3. Selecciona **"🎬 Archivo de Video"**

```
┌────────────────────────────────┐
│  📹 Fuente de Video            │
├────────────────────────────────┤
│ [📷 Webcam] [🎬 Archivo Video]│ ← Click aquí
└────────────────────────────────┘
```

### 2. Cargar Video

1. Click en **"📁 Seleccionar Video"**
2. Selecciona un archivo de video de tu computadora
3. El nombre del archivo aparecerá: `📹 traffic_test.mp4`

```typescript
// Ejemplo de selección
File selected: traffic_test.mp4
Size: 15.2 MB
Type: video/mp4
```

### 3. Configurar Detecciones

```
⚙️ Configuración:
├── Simular Infracciones: ON
├── Límite Velocidad: 60 km/h
├── 🚦 Detección Semáforo: ON
│   └── Línea de Parada (Y): 400
└── 🛣️ Detección de Carriles: ON
```

### 4. Iniciar Detección

- Click en **"🎬 Iniciar Detección con Video"**
- El video comenzará a reproducirse en loop
- Las detecciones se procesarán frame por frame

---

## 🎯 Casos de Uso

### Caso 1: Prueba de Velocidad

**Video Recomendado**: Highway traffic

```yaml
Configuración:
  - Fuente: Archivo de Video
  - Simular Infracciones: ON
  - Límite Velocidad: 80 km/h
  - Infracciones: [speeding]
```

**Resultado Esperado**:
- Vehículos detectados con bounding boxes verdes
- ~33% de vehículos exceden límite
- Infracciones guardadas en BD con tipo `speed`

### Caso 2: Detección de Luz Roja

**Video Recomendado**: Intersection with traffic lights

```yaml
Configuración:
  - Fuente: Archivo de Video
  - 🚦 Detección Semáforo: ON
  - Línea de Parada (Y): 350
  - Infracciones: [red_light]
```

**Resultado Esperado**:
- Estado del semáforo detectado (🔴/🟡/🟢)
- Vehículos cruzando línea de parada en rojo
- Infracción `red_light` con metadata del semáforo

### Caso 3: Invasión de Carril

**Video Recomendado**: Highway with clear lane markings

```yaml
Configuración:
  - Fuente: Archivo de Video
  - 🛣️ Detección de Carriles: ON
  - Infracciones: [wrong_lane]
```

**Resultado Esperado**:
- Carriles detectados (izquierda, derecha, centro)
- Vehículos cruzando líneas
- Infracción `wrong_lane` con distancia y subtipo

### Caso 4: Detección Completa

**Video Recomendado**: Urban traffic (intersections + lanes)

```yaml
Configuración:
  - Fuente: Archivo de Video
  - Simular Infracciones: ON
  - 🚦 Detección Semáforo: ON
  - 🛣️ Detección de Carriles: ON
  - Detectar Placas: ON
  - Infracciones: [speeding, red_light, wrong_lane]
```

**Resultado Esperado**:
- Múltiples tipos de infracciones detectadas
- OCR extrayendo placas
- Dashboard mostrando estadísticas completas

---

## 📊 Interfaz de Usuario

### Controles Disponibles

```
┌─────────────────────────────────────┐
│  ⚙️ Configuración de Detección      │
├─────────────────────────────────────┤
│  📹 Fuente de Video                 │
│  ┌──────────┐  ┌──────────────┐    │
│  │📷 Webcam │  │🎬 Archivo    │    │
│  └──────────┘  └──────────────┘    │
│                                     │
│  📁 Seleccionar Video               │
│  📹 traffic_video.mp4               │
│  🗑️ Limpiar Video                   │
│                                     │
│  Formatos: MP4, AVI, MOV, WebM     │
├─────────────────────────────────────┤
│  Simular Infracciones: [ON]        │
│  Límite Velocidad: 60 km/h         │
│  Detectar Placas: [OFF]             │
│  🚦 Detección Semáforo: [ON]       │
│  🛣️ Detección de Carriles: [ON]   │
└─────────────────────────────────────┘
  
  [🎬 Iniciar Detección con Video]
```

### Overlay de Estadísticas

Durante la reproducción:

```
┌────────────────────┐
│ 🎬 Video File      │ ← Indica modo video
│ 📹 traffic.mp4     │ ← Nombre del archivo
├────────────────────┤
│ Render:    30 FPS  │
│ AI:        15 FPS  │
│ Detecciones:  5    │
├────────────────────┤
│ 🚨 Simulación      │
│    Límite: 60 km/h │
└────────────────────┘
```

---

## 🔧 Implementación Técnica

### Componente React

```typescript
// Estado para archivo de video
const [useVideoFile, setUseVideoFile] = useState(false);
const [videoFile, setVideoFile] = useState<File | null>(null);
const [videoUrl, setVideoUrl] = useState<string | null>(null);

// Refs
const fileInputRef = useRef<HTMLInputElement>(null);
const videoRef = useRef<HTMLVideoElement>(null);

// Manejo de archivo
const handleVideoFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0];
  if (file && file.type.startsWith('video/')) {
    setVideoFile(file);
    const url = URL.createObjectURL(file);
    setVideoUrl(url);
  }
};

// Limpiar archivo
const clearVideoFile = () => {
  if (videoUrl) URL.revokeObjectURL(videoUrl);
  setVideoFile(null);
  setVideoUrl(null);
};
```

### Inicialización del Video

```typescript
const startWebcam = async () => {
  const video = videoRef.current;
  
  if (useVideoFile && videoUrl) {
    // Modo video
    video.src = videoUrl;
    video.loop = true;  // Reproducción continua
    video.muted = true;
    video.playsInline = true;
  } else {
    // Modo webcam
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 } }
    });
    video.srcObject = stream;
  }
  
  await video.play();
};
```

### Limpieza de Recursos

```typescript
// Cleanup on unmount
useEffect(() => {
  return () => {
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
    }
  };
}, [videoUrl]);

// Stop function
const stopWebcam = () => {
  if (videoRef.current) {
    videoRef.current.pause();
    videoRef.current.srcObject = null;
    videoRef.current.src = '';
  }
};
```

---

## 🎬 Videos de Ejemplo Recomendados

### 1. Highway Traffic (Velocidad)
- **Duración**: 30-60 segundos
- **Escena**: Autopista con tráfico fluido
- **Vehículos**: 5-10 simultáneos
- **Resolución**: 1280x720 o superior
- **Link**: [Sample Traffic Videos](https://www.pexels.com/search/videos/highway%20traffic/)

### 2. Traffic Light Intersection (Semáforo)
- **Duración**: 30-60 segundos
- **Escena**: Intersección con semáforo visible
- **Características**: Semáforo en frame superior
- **Vehículos**: Esperando y cruzando
- **Link**: [Traffic Light Videos](https://www.pexels.com/search/videos/traffic%20light/)

### 3. Lane Markings (Carriles)
- **Duración**: 30-60 segundos
- **Escena**: Carretera con líneas visibles
- **Características**: Líneas blancas/amarillas claras
- **Vista**: Desde vehículo (dashcam) o aérea
- **Link**: [Lane Videos](https://www.pexels.com/search/videos/highway%20lanes/)

### 4. Urban Complete (Completo)
- **Duración**: 60-120 segundos
- **Escena**: Tráfico urbano mixto
- **Características**: Intersecciones + carriles + semáforos
- **Vehículos**: Variedad (autos, motos, camiones)
- **Link**: [Urban Traffic Videos](https://www.pexels.com/search/videos/city%20traffic/)

---

## 📝 Logs y Debugging

### Console Logs (F12)

```javascript
// Selección de video
📹 Video file selected: traffic_test.mp4 video/mp4

// Inicio de detección
🎬 Starting detection... (Video file mode)
📹 Loading video file: traffic_test.mp4
✅ Video metadata loaded: 1920 x 1080

// Durante reproducción
📤 Sending frame: {
  size: 45 KB,
  resolution: 640x360,
  wsState: 1
}

📥 Received from server: {
  type: "frame",
  detectionCount: 3,
  infractions: 1,
  lanesDetected: 2
}

🚗 Detections: [
  { type: "car", confidence: "0.89", hasInfraction: true }
]
```

### Backend Logs

```
INFO: 🎬 Processing video frame
INFO: 🚗 Vehicle detected: car (0.89)
INFO: 🚨 INFRACTION: Vehicle exceeds speed limit
INFO: ✅ Infraction registered: INF-20251104-0045
```

---

## ⚠️ Limitaciones y Consideraciones

### Tamaño de Archivo

- **Recomendado**: < 50 MB
- **Máximo**: Depende del navegador
- **Consejo**: Comprimir videos grandes antes de usar

```bash
# Comprimir con FFmpeg
ffmpeg -i input.mp4 -vcodec h264 -acodec mp3 -crf 28 output.mp4
```

### Rendimiento

- Videos 4K pueden reducir FPS
- Recomendado: 1280x720 (HD)
- Procesamiento optimizado a 50% de resolución

### Compatibilidad

| Navegador | Soportado | Formatos |
|-----------|-----------|----------|
| Chrome    | ✅ | MP4, WebM, AVI |
| Firefox   | ✅ | MP4, WebM, OGV |
| Safari    | ✅ | MP4, MOV |
| Edge      | ✅ | MP4, WebM |

### Limitaciones Conocidas

1. **No hay control de reproducción** (play/pause manual)
2. **Loop automático** (no se puede desactivar)
3. **Sin control de velocidad** (reproducción a velocidad normal)
4. **No hay timeline** para saltar a posiciones específicas

---

## 🔮 Mejoras Futuras

### 1. Controles de Reproducción

```typescript
// Propuesta de UI
<div className="video-controls">
  <button onClick={togglePlay}>⏯️ Play/Pause</button>
  <input type="range" onChange={seek} /> {/* Timeline */}
  <select onChange={setSpeed}> {/* Velocidad */}
    <option>0.5x</option>
    <option selected>1x</option>
    <option>2x</option>
  </select>
</div>
```

### 2. Análisis Batch

Procesar múltiples videos en secuencia:

```typescript
const videoQueue = ['video1.mp4', 'video2.mp4', 'video3.mp4'];
// Procesar todos y generar reporte consolidado
```

### 3. Exportar Resultados

Guardar infracciones detectadas en archivo:

```json
{
  "video": "traffic_test.mp4",
  "duration": "60s",
  "infractions": [
    {
      "timestamp": "00:15",
      "type": "red_light",
      "vehicle": "car",
      "confidence": 0.92
    }
  ]
}
```

### 4. Frame-by-Frame Navigation

Navegar frame por frame para análisis detallado:

```typescript
<button onClick={previousFrame}>⏮️ Anterior</button>
<button onClick={nextFrame}>⏭️ Siguiente</button>
```

---

## 🆘 Troubleshooting

### Video no carga

```
❌ Error: Video element not found
```

**Solución**:
1. Verificar formato de video soportado
2. Comprimir video si es muy grande
3. Convertir a MP4 H.264

```bash
ffmpeg -i input.avi -vcodec h264 output.mp4
```

### Detecciones muy lentas

```
AI: 5 FPS (esperado: 15 FPS)
```

**Solución**:
1. Reducir resolución del video
2. Cerrar otras pestañas del navegador
3. Verificar uso de CPU/RAM

### No se detectan infracciones

```
Detecciones: 0
```

**Solución**:
1. Verificar que "Simular Infracciones" esté ON
2. Asegurar que el video tenga vehículos visibles
3. Ajustar umbral de confianza (confidence_threshold)
4. Revisar logs de consola (F12)

### Video se reproduce sin detecciones

```
Render: 30 FPS
AI: 0 FPS
```

**Solución**:
1. Verificar conexión WebSocket al inference service
2. Iniciar inference service: `cd inference-service && uvicorn app.main:app --reload --port 8001`
3. Revisar logs del backend

---

## 📚 Archivos Relacionados

```
frontend-dashboard/
└── src/components/
    └── LocalWebcamDetection.tsx  # Componente principal

docs/
├── GUIA_VIDEO_ARCHIVO.md        # Esta guía
├── DETECCION_SEMAFORO_ROJO.md   # Detección de semáforo
├── DETECCION_INVASION_CARRIL.md # Detección de carriles
└── GUIA_WEBCAM_LOCAL.md         # Guía de webcam

tests/
├── test-red-light.sh            # Test semáforo
├── test-lane-invasion.sh        # Test carriles
└── test-infractions.sh          # Test general
```

---

## ✅ Checklist de Uso

- [ ] Video descargado/preparado (formato MP4 recomendado)
- [ ] Navegador compatible (Chrome/Firefox/Safari/Edge)
- [ ] Inference service corriendo (puerto 8001)
- [ ] Backend Django corriendo (puerto 8000)
- [ ] Dashboard abierto en navegador
- [ ] Fuente seleccionada: "🎬 Archivo de Video"
- [ ] Video cargado correctamente
- [ ] Configuración de detecciones ajustada
- [ ] Consola abierta (F12) para logs
- [ ] Click en "Iniciar Detección con Video"
- [ ] Verificar infracciones en dashboard

---

**Autor**: Sistema BAC - Traffic Infraction Detection System  
**Fecha**: Noviembre 4, 2025  
**Versión**: 1.0.0
