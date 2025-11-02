# Fix Completo - Permisos YOLOv8 y EasyOCR

## 🔴 Errores Encontrados

### Error 1: YOLOv8
```
Permission denied: '/app/models/yolov8n.pt'
```

### Error 2: EasyOCR
```
No such file or directory: '/home/app/.EasyOCR//model/temp.zip'
```

## ✅ Soluciones Aplicadas

**Archivo modificado**: `inference-service/Dockerfile`

### Cambios:

```dockerfile
# ANTES:
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# DESPUÉS:
RUN useradd --create-home --shell /bin/bash app && \
    mkdir -p /app/models && \
    mkdir -p /home/app/.EasyOCR/model && \
    chown -R app:app /app && \
    chown -R app:app /home/app/.EasyOCR
USER app
```

**Explicación**:
1. `/app/models/` - Directorio para YOLOv8 (yolov8n.pt ~6MB)
2. `/home/app/.EasyOCR/model/` - Directorio para modelos OCR (~100MB)
3. Ambos directorios se crean ANTES de cambiar al usuario `app`
4. Permisos correctos asignados con `chown`

## 🚀 Aplicar las Soluciones

### Paso 1: Reconstruir el Servicio

El servicio ya fue reconstruido automáticamente. Si necesitas hacerlo manualmente:

```bash
cd /home/bacsystem/github.com/sistema_in

# Detener y limpiar
docker compose stop inference
docker compose rm -f inference

# Reconstruir
docker compose build inference

# Iniciar
docker compose up -d inference
```

### Paso 2: Esperar a que se Descarguen los Modelos

**Primera vez**: 1-2 minutos
- YOLOv8n.pt: ~6MB
- EasyOCR models (craft, english_g2): ~100MB

```bash
# Ver logs en tiempo real
docker compose logs -f inference
```

### Paso 3: Verificar que Funciona

```bash
cd /home/bacsystem/github.com/sistema_in
bash verify_ml.sh
```

O manualmente:

```bash
# Buscar mensaje de éxito
docker compose logs inference | grep "ML models initialized successfully"

# Verificar archivos descargados
docker exec traffic-inference ls -lh /app/models/
docker exec traffic-inference ls -lh /home/app/.EasyOCR/model/
```

## 📊 Logs Esperados (Correcto)

```
traffic-inference  | {"event": "Initializing ML models...", "level": "info"}

# YOLOv8
traffic-inference  | {"event": "YOLO model not found, downloading...", "level": "info"}
traffic-inference  | Downloading yolov8n.pt: 100%|██████████| 6.23M/6.23M
traffic-inference  | {"event": "YOLO model loaded from /app/models/yolov8n.pt", "level": "info"} ✅

# EasyOCR (puede tardar más)
traffic-inference  | Downloading detection model...
traffic-inference  | Downloading recognition model...
traffic-inference  | {"event": "OCR reader loaded for languages: ['en']", "level": "info"} ✅

# Éxito final
traffic-inference  | {"event": "ML models initialized successfully", "level": "info"} ✅
traffic-inference  | INFO:     Application startup complete.
```

## 🎯 Próximos Pasos

Una vez que veas **"ML models initialized successfully"**:

1. **Abrir el frontend**: http://localhost:3002
2. **Ir a**: "Monitoreo en Tiempo Real"
3. **Seleccionar**: "Cámara Web Local"
4. **Click**: "Iniciar Detección"
5. **Permitir** acceso a la cámara
6. **Esperar** 5-10 segundos

## 🟢 Qué Deberías Ver

### En el Video:
- ✅ **Cuadros verdes** alrededor de vehículos detectados
- ✅ **Etiquetas** con: tipo (car/truck/bus/motorcycle), confianza (%)
- ✅ **Placa** si se detecta (formato Perú: ABC-123)
- ✅ **Velocidad** si se calcula (km/h)
- ✅ **FPS** en tiempo real

### En la Lista de Detecciones:
- ✅ Historial de últimas 10 detecciones
- ✅ Timestamp de cada detección
- ✅ Tipo de objeto/infracción
- ✅ Nivel de confianza

## 🐛 Troubleshooting

### Problema: Sigue sin inicializar

```bash
# Ver todos los errores
docker compose logs inference | grep -i error

# Verificar permisos manualmente
docker exec traffic-inference bash -c "touch /app/models/test.txt && touch /home/app/.EasyOCR/test.txt && echo 'Permisos OK' || echo 'Error de permisos'"
```

### Problema: EasyOCR tarda mucho

**Es normal la primera vez**. EasyOCR descarga ~100MB de modelos:
- `craft_mlt_25k.pth` (detection model)
- `english_g2.pth` (recognition model)

Puede tardar 2-3 minutos en conexiones lentas.

### Problema: WebSocket no conecta

```bash
# Verificar que el servicio esté corriendo
docker compose ps inference

# Debería mostrar: Up (healthy)

# Verificar logs de WebSocket
docker compose logs inference | grep -i websocket
```

### Problema: No detecta vehículos

**Es normal**. YOLOv8 detecta:
- ✅ Coches/automóviles reales
- ✅ Camiones, buses, motocicletas
- ✅ Imágenes/fotos de vehículos
- ✅ Juguetes grandes de vehículos
- ❌ Personas
- ❌ Objetos de oficina
- ❌ Mascotas

**Para probar**: Busca una imagen de un coche en Google y muéstrala a la cámara.

## 📁 Archivos Descargados

Después de la primera inicialización:

```bash
/app/models/
└── yolov8n.pt (6.2MB)

/home/app/.EasyOCR/model/
├── craft_mlt_25k.pth (85MB)
└── english_g2.pth (45MB)
```

Estos archivos se conservan entre reinicios del contenedor (están en volúmenes Docker).

## 🔄 Reiniciar Limpiamente

Si quieres empezar desde cero:

```bash
cd /home/bacsystem/github.com/sistema_in

# Parar todo
docker compose down

# Eliminar volúmenes (esto borra los modelos descargados)
docker volume rm sistema_in_ml_models 2>/dev/null

# Reconstruir e iniciar
docker compose build inference
docker compose up -d

# Los modelos se descargarán de nuevo
```

## ✅ Checklist Final

Antes de probar el frontend:

- [ ] Contenedor inference está "Up"
- [ ] Logs muestran "ML models initialized successfully"
- [ ] Archivo `/app/models/yolov8n.pt` existe (6.2MB)
- [ ] Directorio `/home/app/.EasyOCR/model/` tiene archivos (~130MB)
- [ ] No hay errores en los logs recientes
- [ ] WebSocket está escuchando en puerto 8001

Si todos ✅, probar en: http://localhost:3002 → Monitoreo en Tiempo Real

