# Fix Aplicado: Permisos de Directorio

## 🔴 Error Encontrado

```
Permission denied: '/app/models/yolov8n.pt'
```

**Causa**: El usuario `app` en el contenedor no tenía permisos para escribir en `/app/models/`

## ✅ Solución

**Modificado**: `inference-service/Dockerfile`

**Cambio**:
```dockerfile
# ANTES:
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# DESPUÉS:
RUN useradd --create-home --shell /bin/bash app && \
    mkdir -p /app/models && \
    chown -R app:app /app
```

Ahora se crea el directorio `/app/models` ANTES de cambiar al usuario `app`, asegurando que tenga permisos de escritura.

## 🚀 Aplicar el Fix

### Opción 1: Script Automático (Recomendado)

Abrir **WSL Terminal** y ejecutar:

```bash
cd /home/bacsystem/github.com/sistema_in
bash start_ml_detection.sh
```

Este script:
1. Detiene y elimina el contenedor anterior
2. Reconstruye con permisos correctos
3. Inicia el servicio
4. Espera a que se descargue YOLOv8
5. Verifica que todo funcione

**Tiempo estimado**: 3-5 minutos (primera vez)

### Opción 2: Manual

```bash
cd /home/bacsystem/github.com/sistema_in

# 1. Limpiar contenedor anterior
docker compose stop inference
docker compose rm -f inference

# 2. Reconstruir
docker compose build inference

# 3. Iniciar
docker compose up -d inference

# 4. Ver logs en tiempo real (CTRL+C para salir)
docker compose logs -f inference
```

## 🔍 Verificar que Funciona

**Buscar en los logs**:

```bash
docker compose logs inference | grep "ML models initialized"
```

✅ **Esperado**:
```json
{"event": "ML models initialized successfully", "level": "info"}
```

❌ **Si ves errores**:
```bash
docker compose logs inference | tail -30
```

## 📊 Logs Correctos

Después del fix, deberías ver:

```
traffic-inference  | {"event": "Initializing ML models...", "level": "info"}
traffic-inference  | {"event": "YOLO model not found at /app/models/yolov8n.pt, downloading..."}
traffic-inference  | Downloading yolov8n.pt: 100%|██████████| 6.23M/6.23M [00:01<00:00]
traffic-inference  | {"event": "YOLO model loaded from /app/models/yolov8n.pt", "level": "info"}  ✅
traffic-inference  | {"event": "OCR reader loaded for languages: ['en']", "level": "info"}  ✅
traffic-inference  | {"event": "ML models initialized successfully", "level": "info"}  ✅
traffic-inference  | INFO:     Application startup complete.
```

## 🎯 Próximo Paso

Una vez que veas "ML models initialized successfully":

1. Abrir: http://localhost:3002
2. Ir a: "Monitoreo en Tiempo Real"
3. Seleccionar: "Cámara Web Local"
4. Click: "Iniciar Detección"
5. ✅ Deberías ver **cuadros verdes** en objetos detectados

## 🐛 Si Persiste el Error

Verificar permisos manualmente:

```bash
# Entrar al contenedor
docker exec -it traffic-inference bash

# Verificar permisos del directorio
ls -la /app/

# Debería mostrar:
# drwxr-xr-x  app app  models

# Verificar que puedes escribir
touch /app/models/test.txt
rm /app/models/test.txt

# Si funciona, salir
exit
```

Si no puedes escribir, el fix no se aplicó. Ejecutar:

```bash
docker compose build --no-cache inference
docker compose up -d inference
```

