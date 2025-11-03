# Troubleshooting: Error de Conexión Webcam Local

## Error: "No se pudo conectar con el servicio de detección"

Este error ocurre cuando el componente de webcam local no puede conectarse al servicio de inferencia vía WebSocket.

## Diagnóstico Rápido

### 1. Verificar que el Servicio está Corriendo

```bash
# Verificar si el proceso está activo
ps aux | grep uvicorn | grep 8001

# O verificar el endpoint de salud
curl http://localhost:8001/api/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-02T...",
  "version": "1.0.0",
  "services": {...}
}
```

### 2. Verificar el Puerto

```bash
# Ver qué está escuchando en el puerto 8001
netstat -tlnp | grep 8001
# O en macOS/BSD
lsof -i :8001
```

### 3. Probar WebSocket Manualmente

Abre la consola del navegador (F12) y ejecuta:

```javascript
const ws = new WebSocket('ws://localhost:8001/api/ws/inference');
ws.onopen = () => console.log('✅ Conectado');
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onclose = (e) => console.log('Cerrado:', e.code, e.reason);
```

## Soluciones

### Solución 1: Iniciar el Servicio

Si el servicio no está corriendo:

```bash
# Opción A: Script rápido
cd /home/bacsystem/github.com/sistema_in
./start-inference-service.sh

# Opción B: Manual
cd inference-service
python -m uvicorn app.main:app --reload --port 8001

# Opción C: Con Docker
docker-compose up inference-service
```

### Solución 2: Verificar Configuración de CORS

El servicio debe permitir conexiones WebSocket desde el frontend. Verifica en `inference-service/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Solución 3: Verificar Variables de Entorno

En `frontend-dashboard/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_INFERENCE_WS=ws://localhost:8001
```

Reinicia el servidor de Next.js después de cambiar:

```bash
cd frontend-dashboard
npm run dev
```

### Solución 4: Verificar Firewall

```bash
# Ubuntu/Debian
sudo ufw allow 8001
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --add-port=8001/tcp --permanent
sudo firewall-cmd --reload

# Windows Firewall
# Ir a: Panel de Control → Sistema y Seguridad → Firewall de Windows
# Agregar regla de entrada para puerto 8001
```

### Solución 5: Revisar Logs

```bash
# Logs del servicio de inferencia
tail -f inference-service/logs/app.log

# O si usas Docker
docker-compose logs -f inference-service

# Logs del navegador
# Abrir DevTools (F12) → Console
```

## Errores Comunes y Soluciones

### Error: "WebSocket connection failed: Connection refused"

**Causa**: El servicio no está corriendo en el puerto 8001

**Solución**:
```bash
cd inference-service
python -m uvicorn app.main:app --reload --port 8001
```

### Error: "WebSocket connection failed: 403 Forbidden"

**Causa**: CORS no está configurado correctamente

**Solución**: Verificar configuración de CORS en `main.py`

### Error: "WebSocket closed unexpectedly. Code: 1006"

**Causa**: El servicio se cerró o perdió conexión

**Solución**: 
1. Verificar logs del servidor
2. Reiniciar el servicio
3. Verificar que no hay procesos ocupando el puerto

### Error: "Failed to fetch" al conectar

**Causa**: URL incorrecta o servicio en otra IP

**Solución**:
```javascript
// Verificar URL en LocalWebcamDetection.tsx
const wsUrl = 'ws://localhost:8001/api/ws/inference';
```

## Verificación Completa

Script de verificación completo:

```bash
#!/bin/bash

echo "🔍 Verificando servicios..."

# 1. Backend Django
echo -n "Django (8000): "
curl -s http://localhost:8000/api/health > /dev/null && echo "✅" || echo "❌"

# 2. Inference Service
echo -n "Inference (8001): "
curl -s http://localhost:8001/api/health > /dev/null && echo "✅" || echo "❌"

# 3. Frontend
echo -n "Frontend (3000): "
curl -s http://localhost:3000 > /dev/null && echo "✅" || echo "❌"

# 4. WebSocket
echo -n "WebSocket (8001): "
if nc -z localhost 8001; then
    echo "✅ Puerto abierto"
else
    echo "❌ Puerto cerrado"
fi

# 5. Procesos
echo ""
echo "📊 Procesos activos:"
ps aux | grep -E "uvicorn|django|next" | grep -v grep
```

Guarda como `check-services.sh` y ejecuta:

```bash
chmod +x check-services.sh
./check-services.sh
```

## Reinicio Completo

Si nada funciona, reinicio completo:

```bash
# 1. Detener todo
pkill -f uvicorn
pkill -f "python manage.py"
pkill -f "next dev"

# 2. Limpiar puertos
# Linux
sudo fuser -k 8000/tcp
sudo fuser -k 8001/tcp
sudo fuser -k 3000/tcp

# 3. Iniciar en orden
# Terminal 1: Django
cd backend-django
python manage.py runserver

# Terminal 2: Inference Service
cd inference-service
python -m uvicorn app.main:app --reload --port 8001

# Terminal 3: Frontend
cd frontend-dashboard
npm run dev
```

## Configuración Docker (Alternativa)

Si prefieres usar Docker:

```yaml
# docker-compose.yml
services:
  inference-service:
    build: ./inference-service
    ports:
      - "8001:8001"
    environment:
      - PORT=8001
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Iniciar:

```bash
docker-compose up inference-service
```

## Monitoreo Continuo

Para monitorear el servicio continuamente:

```bash
# Opción 1: watch
watch -n 2 'curl -s http://localhost:8001/api/health | jq .status'

# Opción 2: Loop
while true; do
  curl -s http://localhost:8001/api/health | jq '.status, .uptime_seconds'
  sleep 5
done
```

## Contacto de Soporte

Si el problema persiste:

1. **Revisar logs completos**:
   ```bash
   cat inference-service/logs/app.log
   ```

2. **Capturar error del navegador**:
   - Abrir DevTools (F12)
   - Ir a Console
   - Copiar mensaje de error completo

3. **Información del sistema**:
   ```bash
   uname -a
   python --version
   node --version
   npm --version
   ```

4. **Reportar issue** en el repositorio con:
   - Logs del servidor
   - Logs del navegador
   - Pasos para reproducir
   - Configuración del sistema

---

## Resumen de Comandos Útiles

```bash
# Verificar servicios
curl http://localhost:8001/api/health

# Ver logs en tiempo real
tail -f inference-service/logs/app.log

# Reiniciar servicio
pkill -f uvicorn && python -m uvicorn app.main:app --reload --port 8001

# Verificar puerto
lsof -i :8001

# Probar WebSocket
wscat -c ws://localhost:8001/api/ws/inference
```

**Última actualización**: Noviembre 2, 2025
