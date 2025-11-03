# 🎬 GUÍA DE PRUEBA CON VIDEO - Sistema de Infracciones

## 📋 Configuración Requerida

### 1. Frontend Configuration (Dashboard)

Cuando inicies la detección con video, asegúrate de enviar esta configuración:

```javascript
{
  "simulate_infractions": true,     // ✅ ACTIVAR SIMULACIÓN
  "infractions": ["speeding"],       // ✅ TIPO: exceso de velocidad
  "speed_limit": 60,                  // ⚙️  Límite en km/h
  "confidence_threshold": 0.5,        // ⚙️  Bajado para detectar más vehículos
  "enable_ocr": false,                // ⚙️  Desactivar OCR (más rápido)
  "enable_speed": false               // ⚙️  Usar simulación, no cálculo real
}
```

## 🔍 Logs a Observar

### En el Servicio de Inferencia:
```bash
docker logs -f traffic-inference
```

**Logs Esperados:**

```json
// 1. Frame recibido
{"event": "🖼️  Frame #1: 640x480, config: {...}", ...}

// 2. YOLO detectando
{"event": "🔍 Detecting vehicles with confidence >= 0.5", ...}

// 3. Objetos detectados
{"event": "🔍 YOLO detected 3 objects total", ...}
{"event": "📦 Object #1: class=2, confidence=0.85", ...}
{"event": "📦 Object #2: class=3, confidence=0.72", ...}

// 4. Vehículos filtrados
{"event": "✅ Vehicle detected: car (conf=0.85, bbox=[...])", ...}
{"event": "🚗 Filtered to 2 vehicles from 3 objects", ...}

// 5. Procesamiento de detecciones
{"event": "🔄 Processing 2 vehicle detections...", ...}
{"event": "🚙 Processing vehicle #1: car", ...}

// 6. Simulación de infracción
{"event": "⚙️  Config: simulate=True, infractions=['speeding']", ...}
{"event": "🎲 Vehicle #1: frame=1, idx=0, will_infract=True", ...}
{"event": "🚨 Generated speed: 85.3 km/h (limit: 60 km/h)", ...}
{"event": "🚨 INFRACCIÓN DETECTADA: Vehículo a 85.3 km/h (límite: 60 km/h)", ...}

// 7. Guardado en BD
{"event": "💾 Sending 1 infractions to database...", ...}
{"event": "✅ Guardadas 1 infracciones en la base de datos", ...}
{"event": "  - INF000007: speed | Vehículo: SIN PLACA | Velocidad: 85.3 km/h", ...}

// 8. Resultado enviado
{"event": "📤 Sending result with 2 detections to client", ...}
```

## 🐛 Diagnóstico de Problemas

### Problema 1: "Filtered to 0 vehicles from X objects"

**Causa:** YOLO detecta objetos pero no son vehículos (clases 2, 3, 5, 7)

**Solución:**
- Revisar logs: `📦 Object #X: class=Y`
- Si `class` no es 2 (car), 3 (motorcycle), 5 (bus), 7 (truck) → no se detectará
- Asegurar que el video tenga vehículos visibles

**Clases COCO de YOLO:**
```
0: person
1: bicycle
2: car ✅
3: motorcycle ✅
4: airplane
5: bus ✅
6: train
7: truck ✅
8-79: otros objetos
```

### Problema 2: "YOLO detected 0 objects total"

**Causa:** No hay objetos detectados o confidence muy bajo

**Solución:**
```javascript
// Bajar threshold
{
  "confidence_threshold": 0.3,  // ⬇️ Más bajo = más detecciones
}
```

### Problema 3: Vehículos detectados pero sin infracciones

**Logs esperados:**
```
⚙️  Config: simulate=True, infractions=['speeding']
🎲 Vehicle #1: frame=1, idx=0, will_infract=False
⏭️  Vehicle #1 skipped (no infraction this frame)
```

**Causa:** La probabilidad de infracción es 33% (1 de cada 3)

**Solución:** Esperar más frames, eventualmente detectará infracciones

### Problema 4: "⚠️  Simulation disabled or speeding not in config"

**Causa:** Configuración incorrecta

**Solución:**
```javascript
{
  "simulate_infractions": true,      // ✅ Debe ser true
  "infractions": ["speeding"],        // ✅ Debe incluir "speeding"
}
```

## 📊 Verificación en Base de Datos

### Comando Rápido:
```bash
# Contar infracciones nuevas
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN license_plate_detected = '' THEN 1 END) as sin_placa,
    COUNT(CASE WHEN license_plate_detected != '' THEN 1 END) as con_placa
FROM infractions_infraction 
WHERE detected_at > NOW() - INTERVAL '5 minutes';
"
```

### Ver Últimas Infracciones:
```bash
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    infraction_code,
    ROUND(detected_speed::numeric, 1) || ' km/h' as velocidad,
    COALESCE(NULLIF(license_plate_detected, ''), 'SIN PLACA') as placa,
    TO_CHAR(detected_at, 'HH24:MI:SS') as hora
FROM infractions_infraction 
WHERE detected_at > NOW() - INTERVAL '5 minutes'
ORDER BY detected_at DESC;
"
```

## 🎥 Recomendaciones para el Video

### Características Ideales:
- ✅ Resolución: 640x480 o superior
- ✅ FPS: 15-30 fps
- ✅ Iluminación: Buena, sin sombras excesivas
- ✅ Contenido: Vehículos claramente visibles
- ✅ Ángulo: Vista frontal o lateral de vehículos

### Tipos de Videos que Funcionan Bien:
1. Traffic cam footage
2. Dashcam recordings
3. Videos de calles con tráfico
4. Webcam apuntando a la calle

### Formatos Soportados:
- MP4, AVI, MOV, WebM
- Codec: H.264, VP8, VP9

## 🔧 Ajuste Fino

### Si detecta POCOS vehículos:
```javascript
{
  "confidence_threshold": 0.3,  // ⬇️ Bajar más
}
```

### Si detecta MUCHAS infracciones:
```javascript
// Cambiar lógica en websocket.py línea ~158
if (self.frame_count + idx) % 5 == 0:  // Solo 1 de cada 5
```

### Si NO detecta infracciones:
```javascript
// Cambiar lógica en websocket.py línea ~158
if (self.frame_count + idx) % 2 == 0:  // 1 de cada 2 (50%)
```

## 📞 Comandos de Ayuda

### Reiniciar Todo:
```bash
# Reiniciar inference service
docker restart traffic-inference

# Ver logs en vivo
docker logs -f traffic-inference

# Limpiar infracciones de prueba
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
TRUNCATE TABLE infractions_infractionevent CASCADE;
TRUNCATE TABLE infractions_infraction RESTART IDENTITY CASCADE;
"
```

### Ver Estadísticas:
```bash
curl -s http://localhost:8000/api/infractions/statistics/ | python3 -m json.tool
```

## ✅ Checklist de Prueba

- [ ] Servicio de inferencia corriendo
- [ ] Dashboard frontend abierto
- [ ] Configuración JSON correcta
- [ ] Video cargado (no webcam)
- [ ] Logs de docker visibles en terminal
- [ ] Buscar: "🚨 INFRACCIÓN DETECTADA"
- [ ] Buscar: "✅ Guardadas X infracciones"
- [ ] Verificar en BD con query SQL
- [ ] Ver recuadros ROJOS en video
- [ ] Ver recuadros VERDES en video

## 🎯 Resultado Esperado

Deberías ver:

1. **En el video:**
   - 🟢 Recuadros VERDES para vehículos normales
   - 🔴 Recuadros ROJOS para vehículos con infracción
   - Etiquetas: "INFRACCION: SPEEDING - 85 km/h"

2. **En los logs:**
   - Mensajes con emojis 🚨 🚗 💾 ✅
   - "INFRACCIÓN DETECTADA"
   - "Guardadas X infracciones"

3. **En la base de datos:**
   - Nuevos registros en `infractions_infraction`
   - Nuevos eventos en `infractions_infractionevent`
   - Códigos: INF000007, INF000008, etc.

## 🆘 Si Nada Funciona

1. **Verificar YOLO está detectando:**
```bash
# Debe mostrar: "🔍 YOLO detected X objects total" con X > 0
docker logs --tail 100 traffic-inference | grep "YOLO detected"
```

2. **Verificar configuración llega:**
```bash
# Debe mostrar: "config: {'simulate_infractions': True, ...}"
docker logs --tail 100 traffic-inference | grep "config:"
```

3. **Verificar Django responde:**
```bash
curl http://localhost:8000/api/infractions/
```

4. **Reinicio completo:**
```bash
docker restart traffic-inference
sleep 5
docker logs --tail 50 traffic-inference
```

---

**¡Con estos logs detallados podrás ver exactamente dónde está el problema!** 🔍
