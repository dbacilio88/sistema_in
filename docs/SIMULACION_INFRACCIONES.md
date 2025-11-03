# 🚨 SIMULACIÓN DE INFRACCIONES - GUÍA DE VERIFICACIÓN

## 📋 Resumen de Implementación

Se ha implementado un sistema completo de detección y registro de infracciones de velocidad con las siguientes características:

### ✅ Características Implementadas

1. **Simulación Automática de Infracciones**
   - Detecta vehículos y simula infracciones de velocidad
   - Genera velocidades aleatorias entre 70-100 km/h
   - 33% de probabilidad de infracción por vehículo detectado
   - **Funciona incluso SIN detección de placa**

2. **Visualización Diferenciada**
   - 🟢 **Recuadro VERDE**: Vehículos sin infracciones
   - 🔴 **Recuadro ROJO**: Vehículos con infracciones detectadas
   - Etiquetas con tipo de infracción y velocidad

3. **Almacenamiento en Base de Datos**
   - Guarda TODAS las infracciones en tabla `Infraction`
   - Crea registros en `InfractionEvent` para auditoría
   - **NO requiere placa identificada** para guardar
   - Crea vehículos automáticamente si hay placa

4. **Integración Completa**
   - WebSocket en tiempo real
   - API REST para persistencia
   - Dispositivo por defecto: "Webcam Local"
   - Zona por defecto: "Zona de Prueba"

---

## 🧪 Cómo Probar el Sistema

### Paso 1: Verificar Servicios

```bash
# Verificar que los servicios estén corriendo
docker ps | grep traffic-inference
curl http://localhost:8000/api/infractions/ | jq '.count'
curl http://localhost:8001/api/ | jq '.'
```

### Paso 2: Conectar Webcam

1. Abrir el dashboard: http://localhost:3000
2. Ir a la sección de detección en tiempo real
3. Habilitar la webcam local
4. Configurar detección:
   - ✅ Habilitar `simulate_infractions: true`
   - ✅ Agregar `speeding` a la lista de infracciones
   - ✅ Establecer `speed_limit: 60` (km/h)

### Paso 3: Observar Detecciones

**Lo que verás en el video:**
- 🟢 Vehículos en verde (velocidad normal o sin infracción)
- 🔴 Vehículos en rojo con etiqueta "INFRACCION: SPEEDING - XX km/h"
- Aproximadamente 1 de cada 3 vehículos tendrá infracción

**En los logs del servicio:**
```bash
docker logs -f traffic-inference
```

Buscar mensajes como:
```
"SIMULACIÓN: Vehículo detectado a 85.3 km/h (límite: 60 km/h)"
"✅ Guardadas 1 infracciones en la base de datos"
"- INF000007: speed | Vehículo: SIN PLACA | Velocidad: 85.3 km/h"
```

### Paso 4: Verificar en Base de Datos

```bash
# Ver infracciones recientes
curl http://localhost:8000/api/infractions/recent/ | jq '.[] | {code: .infraction_code, speed: .detected_speed, plate: .license_plate_detected}'

# Ver estadísticas
curl http://localhost:8000/api/infractions/statistics/ | jq '.'

# Consulta directa a PostgreSQL
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    infraction_code,
    infraction_type,
    detected_speed,
    speed_limit,
    license_plate_detected,
    detected_at,
    status
FROM infractions_infraction 
ORDER BY detected_at DESC 
LIMIT 10;
"
```

### Paso 5: Verificar Eventos

```bash
# Ver eventos de infracciones
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    ie.event_type,
    ie.timestamp,
    i.infraction_code,
    i.license_plate_detected
FROM infractions_infractionevent ie
JOIN infractions_infraction i ON ie.infraction_id = i.id
ORDER BY ie.timestamp DESC
LIMIT 10;
"
```

---

## 🔍 Validación de Requisitos

### ✅ Requisito 1: Captura de Infracciones con Webcam
- **IMPLEMENTADO**: Sistema detecta vehículos y simula infracciones de velocidad
- **VERIFICAR**: Logs muestran "SIMULACIÓN: Vehículo detectado a XX km/h"

### ✅ Requisito 2: Guardar Sin Placa Identificada
- **IMPLEMENTADO**: Campo `license_plate_detected` puede estar vacío
- **VERIFICAR**: Query SQL muestra registros con `license_plate_detected = ''`

```sql
SELECT COUNT(*) 
FROM infractions_infraction 
WHERE license_plate_detected = '' OR license_plate_detected IS NULL;
```

### ✅ Requisito 3: Recuadros Rojos para Infracciones
- **IMPLEMENTADO**: 
  - Vehículos sin infracción: `cv2.rectangle(..., (0, 255, 0), 2)` - VERDE
  - Vehículos con infracción: `cv2.rectangle(..., (0, 0, 255), 3)` - ROJO
- **VERIFICAR**: En el video, los vehículos infractores tienen recuadro rojo

### ✅ Requisito 4: Registro en Tabla InfractionEvent
- **IMPLEMENTADO**: Cada infracción crea automáticamente un evento 'detected'
- **VERIFICAR**: Query a `infractions_infractionevent` muestra eventos

---

## 📊 Estructura de Datos Guardados

### Tabla: `infractions_infraction`

```sql
CREATE TABLE infractions_infraction (
    id UUID PRIMARY KEY,
    infraction_code VARCHAR(20) UNIQUE,  -- INF000001, INF000002, etc.
    infraction_type VARCHAR(20),          -- 'speed', 'red_light', etc.
    severity VARCHAR(10),                 -- 'low', 'medium', 'high', 'critical'
    
    device_id UUID,                       -- FK a devices_device
    zone_id UUID,                         -- FK a devices_zone
    
    vehicle_id UUID,                      -- FK a vehicles_vehicle (nullable)
    license_plate_detected VARCHAR(10),   -- Puede estar vacío ""
    license_plate_confidence FLOAT,       -- 0.0 si no hay placa
    
    detected_speed FLOAT,                 -- 85.3, 92.1, etc.
    speed_limit INTEGER,                  -- 60, 40, etc.
    
    status VARCHAR(20),                   -- 'pending', 'validated', etc.
    detected_at TIMESTAMP,
    created_at TIMESTAMP,
    
    evidence_metadata JSONB               -- {source: "webcam_local", ...}
);
```

### Tabla: `infractions_infractionevent`

```sql
CREATE TABLE infractions_infractionevent (
    id UUID PRIMARY KEY,
    infraction_id UUID,                   -- FK a infractions_infraction
    event_type VARCHAR(20),               -- 'detected', 'reviewed', 'validated', etc.
    user_id UUID,                         -- FK a users (nullable)
    notes TEXT,
    metadata JSONB,
    timestamp TIMESTAMP
);
```

---

## 🎯 Ejemplo de Datos Creados

**Infracción con placa:**
```json
{
    "infraction_code": "INF000007",
    "infraction_type": "speed",
    "severity": "high",
    "detected_speed": 85.3,
    "speed_limit": 60,
    "license_plate_detected": "ABC-123",
    "license_plate_confidence": 0.89,
    "status": "pending",
    "device": "Webcam Local",
    "zone": "Zona de Prueba"
}
```

**Infracción SIN placa:**
```json
{
    "infraction_code": "INF000008",
    "infraction_type": "speed",
    "severity": "critical",
    "detected_speed": 97.5,
    "speed_limit": 60,
    "license_plate_detected": "",
    "license_plate_confidence": 0.0,
    "status": "pending",
    "device": "Webcam Local",
    "zone": "Zona de Prueba"
}
```

---

## 🐛 Troubleshooting

### Problema: No se guardan infracciones

**Verificar:**
1. Logs del servicio de inferencia: `docker logs -f traffic-inference`
2. Backend de Django está corriendo: `curl http://localhost:8000/api/`
3. Configuración en el frontend incluye: `simulate_infractions: true`

### Problema: No se ven recuadros rojos

**Verificar:**
1. El frame procesado se está devolviendo correctamente
2. Logs muestran "SIMULACIÓN: Vehículo detectado..."
3. Config incluye `infractions: ['speeding']`

### Problema: Error de secuencia

**Solución:**
```bash
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
CREATE SEQUENCE IF NOT EXISTS infraction_code_seq START 1;
SELECT setval('infraction_code_seq', (SELECT COALESCE(MAX(CAST(SUBSTRING(infraction_code FROM 4) AS INTEGER)), 0) FROM infractions_infraction));
"
```

---

## 📝 Archivos Modificados

1. **backend-django/infractions/services.py** (NUEVO)
   - `InfractionService.bulk_create_from_detections()`
   - Crea infracciones y eventos automáticamente
   - Maneja vehículos con y sin placa

2. **inference-service/app/api/websocket.py**
   - Simulación de infracciones de velocidad
   - Recuadros rojos/verdes según estado
   - Método `_save_infractions_to_database()` mejorado

3. **backend-django/infractions/views.py**
   - Endpoint `/api/infractions/from_detection/` ya existente
   - Acepta detecciones con o sin placa

4. **inference-service/app/services/django_api.py**
   - Método `create_infractions_from_detections()` ya existente
   - Maneja comunicación con backend

---

## ✅ Checklist de Verificación Final

- [ ] Servicios corriendo (inference, django, postgres)
- [ ] Secuencia de infracciones creada
- [ ] Migraciones aplicadas
- [ ] Dispositivo "Webcam Local" existe
- [ ] Zona "Zona de Prueba" existe
- [ ] WebSocket conecta correctamente
- [ ] Se detectan vehículos en webcam
- [ ] Recuadros rojos aparecen para infracciones
- [ ] Logs muestran "Guardadas X infracciones"
- [ ] Query SQL muestra nuevas infracciones
- [ ] Eventos creados en `infractions_infractionevent`

---

## 🎉 Resultado Esperado

Cuando ejecutes el sistema con la webcam:

1. **Visualmente**: Verás vehículos con recuadros verdes y rojos
2. **Logs**: Mensajes de infracciones simuladas y guardadas
3. **Base de Datos**: Nuevos registros en `infractions_infraction`
4. **API**: Endpoint `/api/infractions/recent/` muestra las nuevas infracciones

**Ejemplo de registro completo:**

```bash
# Antes
curl http://localhost:8000/api/infractions/statistics/ | jq '.total_infractions'
# Output: 6

# Después de 1 minuto con webcam
curl http://localhost:8000/api/infractions/statistics/ | jq '.total_infractions'
# Output: 14

# Ver las nuevas infracciones
curl http://localhost:8000/api/infractions/recent/ | jq '.[0:3]'
```

---

## 📞 Soporte

Si encuentras problemas, revisa:
- Logs del contenedor: `docker logs traffic-inference`
- Logs de Django: En el terminal donde corre `python manage.py runserver`
- Estado de la base de datos: Queries SQL de verificación

**¡Sistema listo para demostración!** 🚀
