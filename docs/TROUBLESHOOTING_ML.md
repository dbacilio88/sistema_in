# Solución a Problemas de Detección ML

## 🔴 Problemas Identificados

1. **No aparecen cuadros rojos/verdes**: Los modelos ML NO están cargados correctamente
2. **No se almacenan datos en MinIO**: El bucket `ml-models` no existe

## ✅ Soluciones Aplicadas

### 1. Código Corregido

**Problema**: Había un error en `model_service.py` al cargar YOLO  
**Solución**: ✅ Código corregido y servicio reconstruido completamente

### 2. Servicio Reconstruido

El servicio de inferencia ha sido reconstruido con `--no-cache` para asegurar que use el código corregido.

**Build completado**: ✅ 274 segundos (imagen: sistema_in-inference)

## 📋 Pasos para Activar la Detección

### Paso 1: Iniciar el Servicio de Inferencia

Ejecutar en WSL/Terminal:

```bash
cd /home/bacsystem/github.com/sistema_in
docker compose up -d inference
```

**Esperado**: 
```
[+] Running 1/1
 ✔ Container traffic-inference  Started
```

### Paso 2: Verificar que los Modelos se Carguen

Monitorear los logs en tiempo real:

```bash
docker compose logs -f inference
```

**Buscar estas líneas (debe tardar 10-30 segundos)**:

```
✅ CORRECTO:
{"event": "Initializing ML models...", "level": "info"}
{"event": "YOLO model not found, downloading...", "level": "info"}
Downloading yolov8n.pt: 100%|██████████| 6.23M/6.23M
{"event": "YOLO model loaded from /app/models/yolov8n.pt", "level": "info"}
{"event": "OCR reader loaded for languages: ['en']", "level": "info"}
{"event": "ML models initialized successfully", "level": "info"}
{"event": "Application startup complete", "level": "info"}
```

❌ **SI VES ERRORES** como `"Failed to load YOLO model"`:
- Detener: `docker compose stop inference`
- Eliminar: `docker compose rm -f inference`
- Volver a iniciar: `docker compose up -d inference`

### Paso 3: Crear Bucket de MinIO para Modelos

```bash
# Opción 1: Usar MinIO Web UI
# 1. Abrir http://localhost:9001
# 2. Login: admin / SecurePassword123!
# 3. Click en "Buckets" → "Create Bucket"
# 4. Nombre: ml-models
# 5. Click "Create"

# Opción 2: Línea de comandos (desde WSL)
docker compose run --rm minio-init mc mb --ignore-existing myminio/ml-models
```

### Paso 4: Verificar Estado Completo

```bash
cd /home/bacsystem/github.com/sistema_in

# 1. Ver estado de servicios
docker compose ps inference frontend minio

# Esperado:
# traffic-inference   Up (healthy)
# traffic-frontend    Up 
# traffic-minio       Up (healthy)

# 2. Verificar que YOLO esté cargado
docker compose logs inference | grep "YOLO model loaded"

# Esperado:
# {"event": "YOLO model loaded from /app/models/yolov8n.pt", ...}

# 3. Verificar WebSocket activo
docker compose logs inference | grep WebSocket | tail -5

# 4. Verificar archivo del modelo descargado
docker exec traffic-inference ls -lh /app/models/

# Esperado:
# -rw-r--r-- 1 app app 6.2M Nov  2 XX:XX yolov8n.pt
```

## 🧪 Probar la Detección

### Desde el Frontend

1. **Abrir la aplicación**:
   ```
   http://localhost:3002
   ```

2. **Ir a "Monitoreo en Tiempo Real"**

3. **Configuración**:
   - Cámara: Seleccionar "Cámara Web Local"
   - Límite velocidad: 60 km/h
   - Umbral de confianza: 0.7
   - ✅ Habilitar OCR
   - ✅ Habilitar detección de velocidad
   - Tipos de infracciones: Seleccionar "Exceso de velocidad"

4. **Iniciar Detección**:
   - Click en "Iniciar Detección"
   - Permitir acceso a la cámara cuando el navegador lo solicite
   - **Esperar 5-10 segundos** para que YOLOv8 se inicialice

5. **Verificar que funciona**:
   - ✅ Deberías ver **cuadros verdes** alrededor de objetos detectados como vehículos
   - ✅ Si YOLOv8 detecta un vehículo (car, bus, truck, motorcycle) aparecerá el bounding box
   - ✅ Si detecta una placa, mostrará el texto (formato Perú: ABC-123)
   - ✅ Si estima velocidad > límite, aparecerá **cuadro naranja/rojo** (infracción)

### Verificar en Consola del Navegador

Abrir DevTools (F12) → Console:

```javascript
// Deberías ver mensajes como:
{
  "type": "detection",
  "detections": [
    {
      "id": "...",
      "type": "vehicle",
      "confidence": 0.87,
      "bbox": {"x": 100, "y": 200, "width": 150, "height": 100}
    }
  ],
  "fps": 12.5
}
```

### Verificar Registro en Base de Datos

**Solo si detecta infracciones**:

```bash
# Ver infracciones registradas
curl http://localhost:8000/api/infractions/ | jq

# O en Django Admin
# http://localhost:8000/admin
# Usuario: admin (el que creaste)
# Ir a: Infractions → Infractions
```

## 🐛 Troubleshooting

### Problema: "No aparecen cuadros"

**Causas posibles**:

1. **YOLOv8 no está cargado**
   ```bash
   docker compose logs inference | grep -i error
   ```
   - Si hay errores, reiniciar: `docker compose restart inference`

2. **WebSocket no conectado**
   - Abrir DevTools (F12) → Network → WS
   - Debería aparecer: `ws://localhost:8001/api/ws/inference`
   - Estado: "101 Switching Protocols" (conexión exitosa)

3. **Cámara no está funcionando**
   - Verificar permisos del navegador
   - Probar en Chrome/Edge (mejor soporte WebRTC)
   - Verificar que el video se muestre en pantalla

4. **No detecta nada** (normal si no hay vehículos)
   - YOLOv8 está entrenado para detectar: car, truck, bus, motorcycle
   - Si apuntas a una persona u otro objeto, NO lo detectará
   - **Prueba**: Mostrar una imagen de un coche en tu pantalla

### Problema: "Error de conexión WebSocket"

```bash
# Verificar que inference esté corriendo
docker compose ps inference

# Reiniciar si está caído
docker compose restart inference

# Ver logs de error
docker compose logs inference --tail=50
```

### Problema: "OCR no detecta placas"

**Es normal en MVP**. Causas:
- Iluminación insuficiente
- Cámara muy lejos
- No hay placas vehiculares reales en la escena
- Solo detecta formatos Perú: AAA-123, AB-1234

**Para probar OCR**:
- Imprimir una placa: `ABC-123`
- Mostrar frente a la cámara cuando detecte un "vehículo"

### Problema: "Velocidad siempre 0"

**Es normal**. Necesita:
- Historial de 10+ frames del mismo vehículo
- El vehículo debe moverse (no estar estático)
- Calibración de cámara (pixels → metros)

Para MVP, la velocidad es aproximada y puede no funcionar con la webcam estática.

## 📊 Logs Esperados (Correcto)

```
traffic-inference  | INFO:     Starting Traffic Inference Service v1.0.0
traffic-inference  | {"event": "Initializing ML models...", "level": "info"}
traffic-inference  | {"event": "YOLO model not found, downloading...", "level": "info"}
traffic-inference  | Downloading yolov8n.pt: 100%|██████████| 6.23M/6.23M [00:01<00:00]
traffic-inference  | {"event": "YOLO model loaded from /app/models/yolov8n.pt", "level": "info"}
traffic-inference  | {"event": "OCR reader loaded for languages: ['en']", "level": "info"}
traffic-inference  | {"event": "ML models initialized successfully", "level": "info"}
traffic-inference  | INFO:     Application startup complete.
traffic-inference  | INFO:     Uvicorn running on http://0.0.0.0:8001
```

Luego al conectar desde el frontend:

```
traffic-inference  | INFO:     127.0.0.1:XXXXX - "WebSocket /api/ws/inference" [accepted]
traffic-inference  | {"event": "Client connected", "level": "info"}
traffic-inference  | {"event": "Detection config received", "level": "info"}
traffic-inference  | {"event": "Processing frame", "level": "debug"}
traffic-inference  | {"event": "Detected 2 vehicles", "level": "info"}
```

## 🎯 Checklist de Verificación

Antes de probar:

- [ ] Servicio inference está "Up (healthy)"
- [ ] Logs muestran "ML models initialized successfully"
- [ ] Archivo /app/models/yolov8n.pt existe (6.2MB)
- [ ] WebSocket conecta correctamente
- [ ] Frontend carga sin errores de React
- [ ] Cámara web tiene permisos en el navegador

Para que funcione la detección:

- [ ] Apuntar a un objeto grande (que YOLOv8 pueda confundir con vehículo)
- [ ] Buena iluminación
- [ ] Esperar 5-10 segundos después de "Iniciar Detección"
- [ ] Ver logs en tiempo real: `docker compose logs -f inference`

## 📞 Si Sigue Sin Funcionar

Compartir estos datos:

```bash
# 1. Estado de servicios
docker compose ps inference frontend minio

# 2. Últimos 50 logs de inference
docker compose logs inference --tail=50

# 3. Verificar modelos
docker exec traffic-inference ls -lh /app/models/

# 4. Verificar WebSocket
docker compose logs inference | grep -i websocket | tail -10

# 5. Screenshot de la consola del navegador (F12)
```

---

**IMPORTANTE**: Si después de seguir estos pasos sigues sin ver cuadros, el problema más probable es:
1. YOLOv8 no está detectando ningún vehículo (es normal si no hay coches reales)
2. El WebSocket no está conectado (revisar Network tab en DevTools)
3. Los modelos ML no se cargaron (revisar logs de inference)

