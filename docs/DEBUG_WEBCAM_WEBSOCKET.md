# Debug: Webcam Local - Conexión WebSocket

## Problema: WebSocket se cierra y no captura frames

Este documento te ayudará a diagnosticar por qué el WebSocket se cierra.

## Pasos de Diagnóstico

### 1. Abrir Consola del Navegador

```
Presiona F12 → Pestaña "Console"
```

### 2. Buscar Estos Mensajes

#### ✅ Conexión Exitosa
Deberías ver:
```
✅ WebSocket connected for local webcam
📐 Canvas size set to: 1280 x 720
📤 Sending frame: {size: "45 KB", resolution: "640x360", wsState: 1}
📥 Received from server: {type: undefined, hasDetections: true, detectionCount: 2}
```

#### ❌ Problemas Comunes

**Problema 1: WebSocket se cierra inmediatamente**
```
🔌 WebSocket closed: {code: 1006, reason: "", wasClean: false}
❌ WebSocket closed abnormally
```

**Causa**: Servidor no responde o rechaza conexión
**Solución**: Ver sección "Verificar Servidor"

**Problema 2: Error al enviar frame**
```
❌ Error sending frame: Error: ...
⚠️ WebSocket not ready. State: 3
```

**Causa**: WebSocket cerrado antes de enviar
**Solución**: Ver logs del servidor

**Problema 3: No captura frames**
```
(No aparece "📤 Sending frame")
```

**Causa**: Video no está listo o renderLoop no se inició
**Solución**: Ver sección "Verificar Video"

### 3. Verificar Estado del WebSocket

En la consola del navegador, ejecuta:

```javascript
// Inspeccionar el componente (si tienes React DevTools)
$r.refs.wsRef.current.readyState

// Estados:
// 0 = CONNECTING
// 1 = OPEN (✅ correcto)
// 2 = CLOSING
// 3 = CLOSED (❌ problema)
```

### 4. Verificar Servidor

#### A. Verificar que está corriendo

```bash
# En terminal WSL
curl http://localhost:8001/api/health
```

**Esperado**:
```json
{"status":"healthy",...}
```

#### B. Ver logs del servidor

```bash
# En el terminal donde corre el servicio de inferencia
# Deberías ver:
INFO:     WebSocket client connected
DEBUG:    Received message type: frame
INFO:     Processing frame with config: {...}
```

Si ves:
```
ERROR:    Exception in ASGI application
ERROR:    Invalid frame data
```

→ El servidor rechaza los frames. Ver sección "Formato de Frame"

#### C. Probar WebSocket manualmente

En la consola del navegador:

```javascript
const ws = new WebSocket('ws://localhost:8001/api/ws/inference');
ws.onopen = () => console.log('✅ Conectado');
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onclose = (e) => console.log('🔌 Cerrado:', e.code, e.reason);
ws.onmessage = (e) => console.log('📥 Mensaje:', e.data);

// Enviar ping
ws.send(JSON.stringify({type: 'ping'}));
// Deberías recibir: {"type":"pong"}

// Enviar frame de prueba (pequeño)
const testFrame = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
ws.send(JSON.stringify({
  type: 'frame',
  image: testFrame,
  config: {
    confidence_threshold: 0.7,
    enable_ocr: false
  }
}));
```

### 5. Verificar Video

En la consola del navegador:

```javascript
// Verificar que el video está capturando
const video = document.querySelector('video');
console.log('Video:', {
  readyState: video.readyState,  // Debería ser 4 (HAVE_ENOUGH_DATA)
  videoWidth: video.videoWidth,   // > 0
  videoHeight: video.videoHeight, // > 0
  paused: video.paused,           // false
  srcObject: !!video.srcObject    // true
});

// Verificar que hay stream
if (video.srcObject) {
  const tracks = video.srcObject.getTracks();
  console.log('Tracks:', tracks.map(t => ({
    kind: t.kind,
    enabled: t.enabled,
    readyState: t.readyState
  })));
}
```

**Esperado**:
```javascript
{
  readyState: 4,
  videoWidth: 1280,
  videoHeight: 720,
  paused: false,
  srcObject: true
}
```

### 6. Verificar Canvas

```javascript
const canvas = document.querySelector('canvas');
console.log('Canvas:', {
  width: canvas.width,   // Debería coincidir con video
  height: canvas.height,
  hasContext: !!canvas.getContext('2d')
});

// Verificar que se está dibujando
const ctx = canvas.getContext('2d');
const imageData = ctx.getImageData(0, 0, 1, 1);
console.log('Pixel data:', imageData.data); // No debería ser todo 0
```

## Soluciones por Síntoma

### Síntoma 1: "WebSocket closed: code 1006"

**Diagnóstico**: Cierre anormal, servidor no responde

**Soluciones**:

1. **Reiniciar servidor de inferencia**
   ```bash
   cd inference-service
   pkill -f uvicorn
   python -m uvicorn app.main:app --reload --port 8001
   ```

2. **Verificar puerto correcto**
   ```bash
   netstat -tlnp | grep 8001
   ```

3. **Ver logs del servidor**
   ```bash
   tail -f inference-service/logs/app.log
   ```

### Síntoma 2: Video negro, no captura

**Diagnóstico**: Webcam no está transmitiendo

**Soluciones**:

1. **Verificar permisos de cámara**
   - Chrome: Configuración → Privacidad → Cámara
   - Verificar que localhost está permitido

2. **Probar cámara directamente**
   ```javascript
   navigator.mediaDevices.getUserMedia({video: true})
     .then(stream => console.log('✅ Cámara OK', stream))
     .catch(err => console.error('❌ Error:', err));
   ```

3. **Verificar que hay cámaras disponibles**
   ```javascript
   navigator.mediaDevices.enumerateDevices()
     .then(devices => {
       const cameras = devices.filter(d => d.kind === 'videoinput');
       console.log('Cámaras:', cameras);
     });
   ```

### Síntoma 3: Frames se envían pero no hay respuesta

**Diagnóstico**: Servidor recibe pero no procesa

**Soluciones**:

1. **Verificar formato de frame**
   - En consola, copiar un "📤 Sending frame"
   - Ver que el tamaño no sea excesivo (< 100 KB ideal)
   - Ver que la resolución sea razonable

2. **Revisar configuración**
   ```javascript
   // En LocalWebcamDetection.tsx
   // Verificar que config es válido:
   config: {
     confidence_threshold: 0.7,  // 0-1
     enable_ocr: false,          // boolean
     enable_speed: false,        // boolean
     infractions: [],            // array
     process_interval: 1         // number
   }
   ```

3. **Ver logs del servidor**
   - Debería ver "Processing frame with config"
   - Si ve errores de YOLOv8, el modelo no está cargado

### Síntoma 4: Conecta pero cierra después de primer frame

**Diagnóstico**: Servidor procesa pero falla

**Soluciones**:

1. **Reducir tamaño de frame**
   ```typescript
   // En sendFrameToInference()
   const scale = 0.3; // Reducir a 30%
   canvas.toDataURL('image/jpeg', 0.4); // Calidad más baja
   ```

2. **Aumentar timeout del servidor**
   ```python
   # En inference-service/app/main.py
   app = FastAPI(timeout=60)
   ```

3. **Ver logs detallados**
   ```bash
   # Iniciar servidor con logs debug
   python -m uvicorn app.main:app --reload --port 8001 --log-level debug
   ```

## Modo Debug Avanzado

Activa logs detallados en el componente:

```typescript
// Al inicio de LocalWebcamDetection.tsx
const DEBUG = true;

// En cada función, agregar:
if (DEBUG) console.log('[FUNCTION_NAME]', ...args);
```

## Checklist Completo

- [ ] Servidor de inferencia corriendo en puerto 8001
- [ ] Endpoint /api/health responde con status healthy
- [ ] Webcam permitida en el navegador
- [ ] Video element tiene srcObject y está playing
- [ ] Canvas tiene dimensiones correctas
- [ ] WebSocket se conecta (readyState === 1)
- [ ] Frames se envían (ver logs "📤 Sending frame")
- [ ] Servidor responde (ver logs "📥 Received from server")
- [ ] No hay errores en consola del navegador
- [ ] No hay errores en logs del servidor

## Herramienta de Diagnóstico Automático

Copia y pega en la consola del navegador:

```javascript
async function diagnosticarWebcam() {
  console.log('🔍 Diagnóstico de Webcam Local\n');
  
  // 1. Verificar servidor
  console.log('1️⃣ Verificando servidor...');
  try {
    const health = await fetch('http://localhost:8001/api/health');
    const data = await health.json();
    console.log('✅ Servidor:', data.status);
  } catch (e) {
    console.error('❌ Servidor no responde:', e.message);
    return;
  }
  
  // 2. Verificar cámara
  console.log('\n2️⃣ Verificando cámara...');
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const cameras = devices.filter(d => d.kind === 'videoinput');
    console.log('✅ Cámaras disponibles:', cameras.length);
  } catch (e) {
    console.error('❌ No se puede acceder a cámaras:', e.message);
  }
  
  // 3. Verificar video
  console.log('\n3️⃣ Verificando video...');
  const video = document.querySelector('video');
  if (video) {
    console.log('✅ Video element encontrado');
    console.log('  - readyState:', video.readyState, video.readyState === 4 ? '✅' : '❌');
    console.log('  - dimensions:', video.videoWidth, 'x', video.videoHeight);
    console.log('  - playing:', !video.paused ? '✅' : '❌');
  } else {
    console.error('❌ Video element no encontrado');
  }
  
  // 4. Verificar canvas
  console.log('\n4️⃣ Verificando canvas...');
  const canvas = document.querySelector('canvas');
  if (canvas) {
    console.log('✅ Canvas encontrado');
    console.log('  - dimensions:', canvas.width, 'x', canvas.height);
  } else {
    console.error('❌ Canvas no encontrado');
  }
  
  // 5. Probar WebSocket
  console.log('\n5️⃣ Probando WebSocket...');
  const ws = new WebSocket('ws://localhost:8001/api/ws/inference');
  ws.onopen = () => {
    console.log('✅ WebSocket conectado');
    ws.send(JSON.stringify({type: 'ping'}));
  };
  ws.onmessage = (e) => {
    console.log('✅ WebSocket responde:', e.data);
    ws.close();
  };
  ws.onerror = (e) => {
    console.error('❌ WebSocket error:', e);
  };
  ws.onclose = (e) => {
    if (e.code !== 1000) {
      console.error('❌ WebSocket cerró con código:', e.code);
    }
  };
  
  console.log('\n✅ Diagnóstico completado');
}

diagnosticarWebcam();
```

## Contacto

Si después de todos estos pasos el problema persiste, recopila:

1. Output del script de diagnóstico
2. Logs del servidor (últimas 50 líneas)
3. Screenshots de la consola del navegador
4. Navegador y versión
5. Sistema operativo

---

**Última actualización**: Noviembre 2, 2025
