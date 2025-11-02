# Guía de Verificación y Testing - Integración ML

## Estado Actual

✅ **Código completado**: Toda la integración de YOLOv8, EasyOCR y Django API está implementada  
🔄 **Build en progreso**: El servicio de inferencia se está reconstruyendo con las nuevas dependencias  
⚠️ **Error detectado y corregido**: Problema en la carga del modelo YOLO (línea de export removida)

## Pasos para Verificar

### 1. Verificar que el servicio está corriendo

```bash
cd /home/bacsystem/github.com/sistema_in
docker compose ps inference
```

**Esperado**: El contenedor debe estar en estado "Up" o "Running"

### 2. Verificar logs de inicialización

```bash
docker compose logs inference | grep -E "(Initializing|initialized|YOLO|OCR|ML models)"
```

**Esperado**:
```
INFO: Initializing ML models...
INFO: YOLO model loaded from /app/models/yolov8n.pt
INFO: OCR reader loaded for languages: ['en']
INFO: ML models initialized successfully
INFO: Application startup complete.
```

### 3. Buscar errores

```bash
docker compose logs inference | grep -i error | tail -20
```

**Si hay errores**, revisar:
- Error de "Invalid export format": Ya fue corregido, rebuild necesario
- Error de memoria: Puede ocurrir si no hay suficiente RAM (YOLOv8n + EasyOCR ~ 2GB)
- Error de torch/CUDA: Normal si no hay GPU, debe funcionar en CPU

### 4. Verificar que el modelo se descargó

```bash
docker exec -it traffic-inference ls -lh /app/models/
```

**Esperado**:
```
-rw-r--r-- 1 appuser appuser 6.2M Nov  2 07:29 yolov8n.pt
```

### 5. Probar el endpoint WebSocket

Desde el navegador, abrir la consola de desarrollador (F12) y ejecutar:

```javascript
const ws = new WebSocket('ws://localhost:8001/api/ws/inference');

ws.onopen = () => {
    console.log('✅ WebSocket conectado');
    
    // Enviar configuración
    ws.send(JSON.stringify({
        type: 'config',
        data: {
            detection_types: ['speed'],
            confidence_threshold: 0.7,
            enable_ocr: true,
            enable_speed_detection: true,
            speed_limit: 60
        }
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📩 Mensaje recibido:', data);
};

ws.onerror = (error) => {
    console.error('❌ Error:', error);
};

ws.onclose = () => {
    console.log('🔌 WebSocket cerrado');
};
```

### 6. Probar desde el Frontend

1. **Abrir la aplicación**:
   - URL: http://localhost:3002
   - Navegar a: "Monitoreo en Tiempo Real"

2. **Configurar detección**:
   - Seleccionar: "Cámara Web Local"
   - Establecer límite de velocidad: 60 km/h
   - Habilitar: Detección de velocidad, OCR
   - Tipos de infracciones: Exceso de velocidad

3. **Iniciar detección**:
   - Click en "Iniciar Detección"
   - Permitir acceso a la cámara
   - Observar el video con overlays de detección

4. **Verificar detecciones en tiempo real**:
   - Debe mostrar bounding boxes alrededor de vehículos
   - Si detecta una placa, debe mostrar el texto
   - Si estima velocidad, debe mostrar km/h

### 7. Verificar registro en Base de Datos

```bash
# Acceder al admin de Django
# URL: http://localhost:8000/admin
# Usuario: admin (o el que hayas creado)
# Ir a: Infractions → Infractions
```

**O usar la API**:

```bash
# Listar infracciones
curl http://localhost:8000/api/infractions/ | jq

# Buscar por estado pending
curl "http://localhost:8000/api/infractions/?status=pending" | jq

# Buscar por placa
curl "http://localhost:8000/api/infractions/?search=ABC-123" | jq
```

## Solución de Problemas

### Problema: "YOLO model not found"

**Solución**: El modelo se descarga automáticamente en el primer inicio. Espera 10-30 segundos.

```bash
# Verificar si está descargando
docker compose logs -f inference | grep -i downloading
```

### Problema: "Out of memory" o servicio se reinicia

**Causa**: YOLOv8 + EasyOCR requieren ~2GB RAM

**Solución**:
1. Aumentar memoria de Docker Desktop (Settings → Resources → Memory: 4GB+)
2. O deshabilitar OCR temporalmente:
   ```bash
   # En inference-service/app/core/config.py
   OCR_GPU = False  # Ya está así
   # Y comentar la inicialización de OCR en model_service.py
   ```

### Problema: "Failed to connect to Django"

**Verificar que Django esté corriendo**:

```bash
docker compose ps django

# Debe mostrar: Up (healthy)
```

**Probar conectividad**:

```bash
docker exec -it traffic-inference curl http://django:8000/api/infractions/
```

**Esperado**: JSON con lista de infracciones (puede estar vacía: `[]`)

### Problema: OCR no detecta placas

**Causas comunes**:
1. Iluminación insuficiente → Mejorar luz de la habitación
2. Cámara muy lejos → Acercarse al objeto
3. Placa no en formato Perú → Solo detecta: AAA-123, AB-1234, A12-345
4. Confianza muy baja → El código ya filtra < 0.5

**Debug**:
```bash
# Ver logs de OCR
docker compose logs inference | grep -i ocr
```

### Problema: Velocidad siempre 0 o incorrecta

**Causa**: Necesita calibración de cámara

**Solución temporal**: El sistema usa tracking simple, requiere:
- Mínimo 10 frames de historial
- Vehículo moviéndose (no estático)
- Calibración correcta de `meters_per_pixel`

**Para MVP**: La detección de velocidad es aproximada. Para producción implementar Optical Flow.

## Prueba Manual Completa

### Escenario 1: Detección Básica de Vehículos

1. Abrir http://localhost:3002 → "Monitoreo en Tiempo Real"
2. Seleccionar "Cámara Web Local"
3. Configurar:
   - Límite velocidad: 60 km/h
   - Umbral confianza: 0.7
   - Solo habilitar "Exceso de velocidad"
4. Iniciar detección
5. Mover un objeto grande frente a la cámara (como un coche de juguete)
6. **Esperado**: Debe dibujar un bounding box si lo detecta como vehículo

### Escenario 2: OCR de Placas (Simulación)

**Nota**: Para testing real de OCR, necesitas una imagen de placa peruana impresa

1. Imprimir o mostrar en pantalla una placa: `ABC-123`
2. Configurar:
   - Habilitar OCR
   - Mostrar en el video frente a la cámara
3. **Esperado**: Si la detecta como vehículo y lee la placa, debe mostrar el texto

### Escenario 3: Verificar Registro en BD

1. Realizar detecciones durante 1-2 minutos
2. Abrir Django Admin: http://localhost:8000/admin
3. Navegar a: Infractions
4. **Esperado**: 
   - Ver infracciones creadas automáticamente
   - Cada una con:
     - Código: `INF-SPE-{timestamp}`
     - Tipo: speed
     - Vehículo asociado
     - Velocidad detectada y límite
     - Metadata con bbox y confianza

## Comandos Útiles

```bash
# Rebuild completo del servicio
docker compose build --no-cache inference
docker compose up -d inference

# Ver logs en tiempo real
docker compose logs -f inference

# Reiniciar todos los servicios
docker compose restart

# Ver estado de todos los contenedores
docker compose ps

# Entrar al contenedor de inferencia
docker exec -it traffic-inference bash

# Verificar instalación de paquetes
docker exec -it traffic-inference pip list | grep -E "(ultralytics|easyocr|torch)"

# Ver uso de recursos
docker stats traffic-inference

# Limpiar y reconstruir todo
docker compose down
docker compose build
docker compose up -d
```

## Logs Esperados (Sin Errores)

```
traffic-inference  | INFO:     Starting Traffic Inference Service v1.0.0
traffic-inference  | {"event": "Initializing ML models...", "level": "info"}
traffic-inference  | {"event": "YOLO model not found, downloading...", "level": "info"}
traffic-inference  | Downloading yolov8n.pt: 100%|██████████| 6.23M/6.23M [00:01<00:00, 5.2MB/s]
traffic-inference  | {"event": "YOLO model loaded from /app/models/yolov8n.pt", "level": "info"}
traffic-inference  | {"event": "OCR reader loaded for languages: ['en']", "level": "info"}
traffic-inference  | {"event": "ML models initialized successfully", "level": "info"}
traffic-inference  | INFO:     Application startup complete.
traffic-inference  | INFO:     Uvicorn running on http://0.0.0.0:8001
```

## Siguiente Fase: Optimización

Una vez verificado que funciona:

### 1. Calibración de Cámara
- Medir distancia real vs píxeles
- Actualizar `CAMERA_CALIBRATION` en config.py

### 2. Fine-tuning de Umbrales
- Ajustar `YOLO_CONFIDENCE_THRESHOLD` según false positives
- Ajustar mínimo de OCR confidence

### 3. Entrenamiento Custom (Opcional)
- Recopilar dataset local (vehículos y placas peruanas)
- Fine-tune YOLOv8 con `yolo train`
- Fine-tune EasyOCR con dataset de placas

### 4. Integración de Modelos Adicionales
- Detección de semáforos (traffic_light.pt)
- Segmentación de carriles (lane_detection.pt)
- Clasificación de color de vehículo

### 5. Mejoras de Rendimiento
- Activar GPU si está disponible
- Implementar batch processing
- Optimizar con TensorRT/ONNX

---

**Documentación Completa**:
- `docs/ML_INTEGRATION.md` - Detalles técnicos de la integración
- `docs/INTEGRATION_SUMMARY.md` - Resumen de cambios realizados
- Este archivo - Guía de verificación y testing

