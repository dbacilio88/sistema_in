# 🔍 Troubleshooting: Conexión con Base de Datos

## 🚨 Problema: Infracciones Detectadas pero no se Guardan

### Síntomas
```javascript
// En consola del navegador (F12)
🚨 INFRACTIONS DETECTED: 2
   Infraction #1: Object
   Infraction #2: Object
```

Pero no aparecen en la base de datos.

---

## ✅ Pasos de Verificación

### 1. Verificar Servicios Corriendo

```bash
# Backend Django
curl http://localhost:8000/api/health/

# Inference Service
curl http://localhost:8001/health

# Base de datos PostgreSQL
docker ps | grep postgres
```

**Resultado Esperado**:
- ✅ Django: `{"status": "ok"}`
- ✅ Inference: `{"status": "healthy"}`
- ✅ PostgreSQL: Contenedor corriendo

---

### 2. Ejecutar Script de Verificación

```bash
chmod +x verify-database-connection.sh
./verify-database-connection.sh
```

Este script:
- Verifica que los servicios estén corriendo
- Prueba crear infracciones por API
- Consulta la base de datos directamente
- Muestra las últimas infracciones guardadas

---

### 3. Verificar Configuración de Django API URL

**El problema más común es la URL incorrecta**

#### En Desarrollo (localhost):
```bash
# inference-service/.env
DJANGO_API_URL=http://localhost:8000
```

#### En Docker Compose:
```bash
# inference-service/.env
DJANGO_API_URL=http://django:8000
```

**Crear archivo `.env` si no existe:**
```bash
cd inference-service
cp .env.example .env
# Editar .env y configurar DJANGO_API_URL=http://localhost:8000
```

---

### 4. Revisar Logs del Inference Service

```bash
# Terminal donde corre inference service
# Buscar estos logs:

🔗 DjangoAPIService initialized with URL: http://localhost:8000
⏱️  Timeout: 30s

📤 Attempting to create infraction: type=speed, plate=ABC-123

# Si hay error de conexión:
🔌 Connection error to Django API (http://localhost:8000): ...
⚠️ Verifica que el backend Django esté corriendo en el puerto correcto
```

---

### 5. Probar API de Django Manualmente

```bash
# Test 1: Health check
curl http://localhost:8000/api/health/

# Test 2: Listar infracciones existentes
curl http://localhost:8000/api/infractions/

# Test 3: Crear infracción manual
curl -X POST http://localhost:8000/api/infractions/ \
  -H "Content-Type: application/json" \
  -d '{
    "infraction_type": "speed",
    "detected_at": "2025-11-04T10:00:00Z",
    "severity": "high",
    "status": "pending",
    "license_plate_detected": "TEST-123",
    "detected_speed": 120.0,
    "speed_limit": 60
  }'
```

**Resultado Esperado**:
```json
{
  "id": 1,
  "infraction_code": "INF-20251104-0001",
  "infraction_type": "speed",
  "severity": "high",
  ...
}
```

---

### 6. Verificar Base de Datos Directamente

```bash
# Conectar a PostgreSQL
docker exec -it <postgres-container> psql -U postgres -d traffic_db

# Dentro de psql:
\dt  # Listar tablas

SELECT COUNT(*) FROM infractions_infraction;  # Contar infracciones

SELECT infraction_code, infraction_type, severity, detected_at 
FROM infractions_infraction 
ORDER BY detected_at DESC 
LIMIT 5;  # Ver últimas 5
```

---

## 🐛 Errores Comunes

### Error 1: Connection Refused

```
🔌 Connection error to Django API (http://localhost:8000): Connection refused
```

**Causa**: Backend Django no está corriendo

**Solución**:
```bash
cd backend-django
python manage.py runserver
```

---

### Error 2: URL Incorrecta (404)

```
❌ Failed to create infraction: status=404
```

**Causa**: URL del endpoint incorrecta

**Verificar**:
```python
# inference-service/app/services/django_api.py
url = f"{self.base_url}/api/infractions/"
# Debe ser: http://localhost:8000/api/infractions/
```

---

### Error 3: Timeout

```
⏱️ Timeout connecting to Django API
```

**Causa**: Django muy lento o no responde

**Soluciones**:
1. Aumentar timeout:
   ```bash
   # .env
   DJANGO_API_TIMEOUT=60
   ```

2. Verificar logs de Django:
   ```bash
   cd backend-django
   python manage.py runserver --verbosity=2
   ```

---

### Error 4: Validation Error (400)

```
❌ Failed to create infraction: status=400
Response: {"field": ["This field is required"]}
```

**Causa**: Datos faltantes en la petición

**Verificar campos requeridos**:
```python
# Mínimo requerido:
{
    "infraction_type": "speed",  # speed, red_light, wrong_lane
    "detected_at": "2025-11-04T10:00:00Z",  # ISO format
    "severity": "high",  # low, medium, high, critical
    "status": "pending"  # pending, validated, rejected
}
```

---

### Error 5: Database Connection Error

```
django.db.utils.OperationalError: could not connect to server
```

**Soluciones**:

1. Verificar PostgreSQL corriendo:
   ```bash
   docker ps | grep postgres
   ```

2. Verificar configuración en `backend-django/config/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'traffic_db',
           'USER': 'postgres',
           'PASSWORD': 'postgres',
           'HOST': 'localhost',  # o 'postgres' en Docker
           'PORT': '5432',
       }
   }
   ```

3. Ejecutar migraciones:
   ```bash
   cd backend-django
   python manage.py migrate
   ```

---

## 📊 Verificar Datos en Frontend

### Console Logs Mejorados (F12)

```javascript
// Ahora los logs muestran JSON completo:
🚨 INFRACTIONS DETECTED: 2
   Infraction #1: {
     "type": "speed",
     "vehicle": "car",
     "speed": 95,
     "speedLimit": 60,
     "plate": "ABC-123",
     "confidence": "0.92",
     "infractionData": {
       "speed_limit": 60,
       "detected_speed": 95
     }
   }
```

---

## 🔧 Configuración Recomendada para Desarrollo

### inference-service/.env
```bash
DJANGO_API_URL=http://localhost:8000
DJANGO_API_TIMEOUT=30
LOG_LEVEL=INFO
LOG_FORMAT=console  # Mejor para debugging
DEBUG=true
```

### backend-django/config/settings.py
```python
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'traffic_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

---

## ✅ Checklist de Verificación

- [ ] Backend Django corriendo en puerto 8000
- [ ] Inference Service corriendo en puerto 8001
- [ ] PostgreSQL corriendo (Docker o local)
- [ ] Archivo `.env` configurado en inference-service
- [ ] `DJANGO_API_URL=http://localhost:8000` en .env
- [ ] Migraciones aplicadas: `python manage.py migrate`
- [ ] API responde: `curl http://localhost:8000/api/infractions/`
- [ ] Logs muestran: `🔗 DjangoAPIService initialized with URL: http://localhost:8000`
- [ ] Frontend muestra logs detallados en consola (F12)
- [ ] Script de verificación ejecutado: `./verify-database-connection.sh`

---

## 🎯 Test Rápido

```bash
# Test completo en 3 pasos:

# 1. Verificar servicios
curl http://localhost:8000/api/health/
curl http://localhost:8001/health

# 2. Crear infracción de prueba
curl -X POST http://localhost:8000/api/infractions/ \
  -H "Content-Type: application/json" \
  -d '{"infraction_type":"speed","detected_at":"2025-11-04T10:00:00Z","severity":"high","status":"pending","detected_speed":120,"speed_limit":60}'

# 3. Verificar que se guardó
curl http://localhost:8000/api/infractions/ | grep -o "infraction_code" | wc -l
```

---

## 📞 Soporte

Si después de seguir todos los pasos sigue sin funcionar:

1. **Capturar logs completos**:
   ```bash
   # Terminal 1 (Django)
   python manage.py runserver > django.log 2>&1
   
   # Terminal 2 (Inference)
   uvicorn app.main:app --reload > inference.log 2>&1
   ```

2. **Ejecutar en modo debug**:
   ```bash
   # inference-service/.env
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

3. **Revisar documentación**:
   - `docs/TROUBLESHOOTING_WEBCAM.md`
   - `docs/BACKEND-DJANGO.md`
   - `docs/INFERENCE-SERVICE.md`

---

**Autor**: Sistema BAC - Traffic Infraction Detection System  
**Fecha**: Noviembre 4, 2025  
**Versión**: 1.0.0
