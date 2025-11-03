# 🚀 GUÍA RÁPIDA - Sistema de Infracciones

## ⚡ Inicio Rápido (5 minutos)

### 1. Verificar Servicios
```bash
# Inference service (debe estar corriendo)
docker ps | grep traffic-inference

# Django backend
curl http://localhost:8000/api/infractions/ | head -50

# PostgreSQL
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction;"
```

### 2. Configurar Frontend
Abrir dashboard en: `http://localhost:3000`

**Configuración de Detección:**
```javascript
{
  "simulate_infractions": true,  // ← IMPORTANTE: Activar simulación
  "infractions": ["speeding"],   // ← Tipo de infracciones a detectar
  "speed_limit": 60,              // ← Límite en km/h
  "enable_ocr": false,            // ← Opcional: OCR de placas
  "confidence_threshold": 0.7     // ← Confianza mínima YOLO
}
```

### 3. Conectar Webcam
1. Click en botón "Iniciar Detección"
2. Permitir acceso a cámara
3. ¡Ver detecciones en tiempo real!

---

## 🎨 Qué Verás

### En el Video:
- 🟢 **Recuadros VERDES**: Vehículos normales (sin infracción)
- 🔴 **Recuadros ROJOS**: Vehículos con infracciones
- 🏷️ **Etiquetas**: Tipo de vehículo + velocidad

**Ejemplo:**
```
INFRACCION: SPEEDING - 85 km/h  (recuadro rojo)
CAR - 55 km/h                    (recuadro verde)
TRUCK - 92 km/h                  (recuadro rojo)
```

### En los Logs:
```bash
docker logs -f traffic-inference
```

Buscar:
```
SIMULACIÓN: Vehículo detectado a 85.3 km/h (límite: 60 km/h)
✅ Guardadas 1 infracciones en la base de datos
  - INF000007: speed | Vehículo: SIN PLACA | Velocidad: 85.3 km/h
```

---

## 🔍 Verificar en Base de Datos

### Contar Infracciones
```bash
curl http://localhost:8000/api/infractions/statistics/
```

### Ver Últimas Infracciones
```bash
curl http://localhost:8000/api/infractions/recent/
```

### Query SQL Directo
```sql
-- Últimas 10 infracciones
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    infraction_code,
    detected_speed || ' km/h' as velocidad,
    COALESCE(license_plate_detected, 'SIN PLACA') as placa,
    TO_CHAR(detected_at, 'HH24:MI:SS') as hora
FROM infractions_infraction 
ORDER BY detected_at DESC 
LIMIT 10;
"
```

### Infracciones SIN Placa
```sql
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT COUNT(*) as sin_placa
FROM infractions_infraction 
WHERE license_plate_detected = '' OR license_plate_detected IS NULL;
"
```

---

## 🎯 Comportamiento Esperado

### Simulación Automática:
- **Probabilidad**: 33% de los vehículos detectados tendrán infracción
- **Velocidades**: Aleatorias entre 70-100 km/h
- **Límite**: Configurable (por defecto 60 km/h)
- **Guardado**: Automático en segundo plano

### Ejemplo de Sesión (1 minuto):
```
Vehículos detectados: 12
Infracciones generadas: 4 (33%)
Infracciones guardadas: 4
  - 2 SIN placa
  - 2 CON placa simulada
```

---

## 🔧 Troubleshooting Rápido

### Problema: No veo recuadros rojos
**Solución:**
1. Verificar config: `simulate_infractions: true`
2. Verificar: `infractions: ["speeding"]`
3. Logs: Buscar "SIMULACIÓN:"

### Problema: No se guardan en BD
**Solución:**
1. Django corriendo: `curl http://localhost:8000/api/`
2. Logs inference: `docker logs --tail 50 traffic-inference`
3. Verificar secuencia: Ver abajo ⬇️

### Problema: Error de secuencia
**Solución:**
```bash
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
CREATE SEQUENCE IF NOT EXISTS infraction_code_seq START 1;
SELECT setval('infraction_code_seq', 
  (SELECT COALESCE(MAX(CAST(SUBSTRING(infraction_code FROM 4) AS INTEGER)), 0) 
   FROM infractions_infraction)
);
"
```

### Problema: Django no responde
**Solución:**
```bash
# Encontrar PID
ps aux | grep "manage.py runserver" | grep -v grep

# Reiniciar (cambiar PID)
sudo kill -9 PID
cd /home/bacsystem/github.com/sistema_in/backend-django
python manage.py runserver 0.0.0.0:8000
```

---

## 📊 Verificación Completa

### Checklist:
- [ ] Inference service corriendo
- [ ] Django backend corriendo  
- [ ] PostgreSQL conectado
- [ ] Secuencia creada
- [ ] Migraciones aplicadas
- [ ] Frontend cargando
- [ ] Webcam funcionando
- [ ] Recuadros rojos visibles
- [ ] Logs muestran "Guardadas X infracciones"
- [ ] Query SQL muestra nuevas infracciones

### Comando de Verificación Completo:
```bash
#!/bin/bash
echo "=== VERIFICACIÓN SISTEMA INFRACCIONES ==="

echo -n "1. Inference service: "
docker ps | grep -q traffic-inference && echo "✅ OK" || echo "❌ FAIL"

echo -n "2. Django backend: "
curl -s http://localhost:8000/api/ > /dev/null && echo "✅ OK" || echo "❌ FAIL"

echo -n "3. PostgreSQL: "
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT 1;" > /dev/null 2>&1 && echo "✅ OK" || echo "❌ FAIL"

echo -n "4. Secuencia: "
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT EXISTS(SELECT 1 FROM pg_sequences WHERE sequencename='infraction_code_seq');" -t | grep -q t && echo "✅ OK" || echo "❌ FAIL"

echo "5. Total infracciones:"
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction;" -t

echo "=== VERIFICACIÓN COMPLETA ==="
```

---

## 📱 Uso en Producción

### Desactivar Simulación (Velocidad Real):
```javascript
{
  "simulate_infractions": false,  // ← Desactivar simulación
  "enable_speed": true,           // ← Activar cálculo real
  "infractions": ["speeding"],
  "speed_limit": 60
}
```

**Nota:** Requiere calibración de cámara y tracking mejorado.

### Activar OCR de Placas:
```javascript
{
  "enable_ocr": true,             // ← Activar OCR
  "ocr_confidence": 0.7,          // ← Confianza mínima
  "simulate_infractions": true
}
```

---

## 🎓 Ejemplos de Uso

### Ejemplo 1: Monitoreo de Zona Escolar
```javascript
{
  "simulate_infractions": true,
  "infractions": ["speeding"],
  "speed_limit": 30,              // ← Límite bajo
  "enable_ocr": true
}
```

### Ejemplo 2: Autopista
```javascript
{
  "simulate_infractions": true,
  "infractions": ["speeding"],
  "speed_limit": 100,             // ← Límite alto
  "confidence_threshold": 0.8
}
```

### Ejemplo 3: Multi-Infracción
```javascript
{
  "simulate_infractions": false,
  "infractions": ["speeding", "red_light", "wrong_lane"],
  "speed_limit": 60,
  "enable_ocr": true
}
```

---

## 📞 Ayuda Rápida

**Documentación Completa:**
- `docs/SIMULACION_INFRACCIONES.md` - Guía detallada
- `docs/RESUMEN_INFRACCIONES.md` - Resumen técnico
- `docs/DETECCIONES_POR_TIPO.md` - Sistema de detecciones

**Logs Importantes:**
```bash
# Inference service
docker logs -f traffic-inference

# Django
# (ver terminal donde corre manage.py runserver)

# PostgreSQL
docker logs -f traffic-postgres
```

**Comandos Útiles:**
```bash
# Reiniciar inference
docker restart traffic-inference

# Ver última infracción
curl http://localhost:8000/api/infractions/recent/ | head -100

# Limpiar infracciones de prueba
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
DELETE FROM infractions_infractionevent WHERE infraction_id IN (
  SELECT id FROM infractions_infraction WHERE evidence_metadata->>'source' = 'test_script'
);
DELETE FROM infractions_infraction WHERE evidence_metadata->>'source' = 'test_script';
"
```

---

## ✅ Todo Listo!

El sistema está **completamente funcional** y listo para usar. 

**Siguientes pasos:**
1. Abrir dashboard: http://localhost:3000
2. Configurar detección (ver configuración arriba)
3. Conectar webcam
4. ¡Observar detecciones en tiempo real!

**¿Problemas?** → Ver sección Troubleshooting o logs

**¡Éxito!** 🎉
