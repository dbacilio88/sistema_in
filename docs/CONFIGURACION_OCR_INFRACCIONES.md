# Configuración de Detección OCR - Guía de Uso

## 📋 Configuraciones por Tipo de Infracción

### 1. Exceso de Velocidad (Speeding)

#### Configuración Mínima
```json
{
  "infractions": ["speeding"],
  "confidence_threshold": 0.5,
  "enable_speed": true,
  "speed_limit": 60,
  "simulate_infractions": true
}
```

#### Logs Esperados
```
🚨 INFRACTION DETECTED: speed for car
   🎯 Infraction Type: speed
🔤 Attempting OCR for SPEED infraction...
✅ PLATE DETECTED for SPEED: 'ABC-123' (confidence: 0.78)
```

#### Requisitos
- ✅ `"speeding"` en array `infractions`
- ✅ `enable_speed: true`
- ✅ `speed_limit` definido (ej: 60 km/h)
- ✅ `simulate_infractions: true` (para pruebas) O tracking real

---

### 2. Semáforo Rojo (Red Light)

#### Configuración Mínima
```json
{
  "infractions": ["red_light"],
  "confidence_threshold": 0.5,
  "traffic_light_state": "red",
  "stop_line_y": 400
}
```

#### Logs Esperados
```
🚦 Traffic light detected: red (confidence=0.85)
🚨 INFRACTION DETECTED: red_light for car
   🎯 Infraction Type: red_light
🔤 Attempting OCR for RED_LIGHT infraction...
✅ PLATE DETECTED for RED_LIGHT: 'XYZ-789' (confidence: 0.71)
```

#### Requisitos
- ✅ `"red_light"` en array `infractions`
- ✅ `traffic_light_state: "red"` (detectado automáticamente)
- ✅ `stop_line_y` definido (coordenada Y de la línea de parada)

#### Calibración de `stop_line_y`
1. Abrir video en reproductor
2. Identificar línea de parada (rayado blanco)
3. Medir coordenada Y (desde arriba)
4. Configurar en WebSocket

**Ejemplo:**
- Video 1920x1080: `stop_line_y: 650`
- Video 1280x720: `stop_line_y: 450`
- Video 854x480: `stop_line_y: 300`

---

### 3. Invasión de Carril (Wrong Lane)

#### Configuración Mínima
```json
{
  "infractions": ["wrong_lane"],
  "confidence_threshold": 0.5,
  "enable_lane_detection": true,
  "lane_roi": [[0, 480], [640, 480], [640, 200], [0, 200]]
}
```

#### Logs Esperados
```
🛣️ Lanes detected: 2 lanes (center: true)
🚨 LANE INVASION: car crossed LEFT line (distance: 145px)
🚨 INFRACTION DETECTED: wrong_lane for car
   🎯 Infraction Type: wrong_lane
🔤 Attempting OCR for WRONG_LANE infraction...
✅ PLATE DETECTED for WRONG_LANE: 'B7J-482' (confidence: 0.64)
```

#### Requisitos
- ✅ `"wrong_lane"` en array `infractions`
- ✅ `enable_lane_detection: true`
- ✅ `lane_roi` definido (región de interés para detección)
- ✅ **Video con líneas de carril VISIBLES** (blancas/amarillas)

#### ⚠️ Problema Común: "has_lanes={}"
Si ves este log, significa que NO se detectaron líneas:
```
🔍 Checking lane invasion: lane_detection=True, has_lanes={}
```

**Soluciones:**
1. Verificar que el video tenga líneas claras
2. Ajustar `lane_roi` para incluir zona con líneas
3. Probar con otro video con mejor marcado de carril

---

### 4. Múltiples Infracciones

#### Configuración Completa
```json
{
  "infractions": ["speeding", "wrong_lane", "red_light"],
  "confidence_threshold": 0.5,
  "enable_speed": true,
  "enable_lane_detection": true,
  "speed_limit": 60,
  "stop_line_y": 400,
  "simulate_infractions": true,
  "ocr_all_vehicles": false
}
```

#### Prioridad de Detección
El sistema verifica en este orden:
1. **Speeding** (si `enable_speed: true`)
2. **Red Light** (si `traffic_light_state: "red"`)
3. **Wrong Lane** (si `enable_lane_detection: true` y hay líneas)

**Nota:** Solo se guarda **UNA infracción por vehículo** (la primera detectada)

---

## 🎛️ Parámetros Opcionales Avanzados

### `ocr_all_vehicles` (boolean, default: false)
Ejecutar OCR en **todos los vehículos**, no solo en infracciones.

```json
{
  "ocr_all_vehicles": true
}
```

**⚠️ Advertencia:** Aumenta significativamente el tiempo de procesamiento.

**Uso recomendado:**
- ✅ Para sistemas de registro de tráfico (sin infracciones)
- ✅ Para análisis de flujo vehicular
- ❌ NO recomendado para detección de infracciones (innecesario)

---

## 🧪 Ejemplos de Configuración por Escenario

### Escenario 1: Pruebas Rápidas (Simulación)
```typescript
const config = {
  infractions: ['speeding', 'wrong_lane'],
  confidence_threshold: 0.5,
  enable_speed: true,
  speed_limit: 60,
  simulate_infractions: true, // ✅ Genera infracciones aleatorias
  ocr_all_vehicles: false
};
```

**Resultado:** Infracciones aleatorias con placas detectadas automáticamente.

---

### Escenario 2: Producción - Exceso de Velocidad
```typescript
const config = {
  infractions: ['speeding'],
  confidence_threshold: 0.6,
  enable_speed: true,
  speed_limit: 60,
  simulate_infractions: false, // ✅ Modo real
  ocr_all_vehicles: false
};
```

**Requisitos:**
- Cámara calibrada para medir velocidad
- Sistema de tracking funcional

---

### Escenario 3: Producción - Semáforo Rojo
```typescript
const config = {
  infractions: ['red_light'],
  confidence_threshold: 0.6,
  stop_line_y: 450, // ✅ Calibrar según video
  ocr_all_vehicles: false
};
```

**Requisitos:**
- Semáforo visible en frame
- Línea de parada identificable
- Calibración de `stop_line_y`

---

### Escenario 4: Producción - Invasión de Carril
```typescript
const config = {
  infractions: ['wrong_lane'],
  confidence_threshold: 0.6,
  enable_lane_detection: true,
  lane_roi: [[0, 480], [640, 480], [640, 200], [0, 200]], // ✅ Calibrar según video
  ocr_all_vehicles: false
};
```

**Requisitos:**
- Video con líneas de carril CLARAS (blancas/amarillas)
- Resolución mínima 720p
- Buena iluminación
- `lane_roi` calibrado para incluir carriles

---

### Escenario 5: Testing Completo
```typescript
const config = {
  infractions: ['speeding', 'wrong_lane', 'red_light'],
  confidence_threshold: 0.5,
  enable_speed: true,
  enable_lane_detection: true,
  speed_limit: 60,
  stop_line_y: 400,
  simulate_infractions: true, // ✅ Para testing
  ocr_all_vehicles: false
};
```

**Uso:** Verificar que todos los tipos de infracciones funcionen correctamente.

---

## 📊 Verificación de Funcionamiento

### 1. Verificar que OCR se ejecuta
```bash
docker logs inference-service --tail 100 | grep "PLATE DETECTED"
```

**Salida esperada:**
```
✅ PLATE DETECTED for SPEED: 'ABC-123' (confidence: 0.78)
✅ PLATE DETECTED for RED_LIGHT: 'XYZ-789' (confidence: 0.71)
✅ PLATE DETECTED for WRONG_LANE: 'B7J-482' (confidence: 0.64)
```

### 2. Verificar infracciones guardadas
```bash
docker logs inference-service --tail 100 | grep "NEW UNIQUE INFRACTION"
```

**Salida esperada:**
```
✅ ✨ NEW UNIQUE INFRACTION REGISTERED: speed for plate 'ABC-123'
✅ ✨ NEW UNIQUE INFRACTION REGISTERED: red_light for plate 'XYZ-789'
```

### 3. Verificar duplicados evitados
```bash
docker logs inference-service --tail 100 | grep "DUPLICATE"
```

**Salida esperada:**
```
⏭️ 🚫 DUPLICATE DETECTED: Plate 'ABC-123' already has speed infraction from 15 frames ago
```

---

## 🔧 Troubleshooting

### Problema: OCR no se ejecuta

**Síntoma:**
```
No aparecen logs de "Attempting OCR"
```

**Causas posibles:**
1. ❌ No se detectan infracciones
2. ❌ Tipo de infracción no habilitado en `infractions` array
3. ❌ Requisitos de infracción no cumplidos

**Solución:**
```bash
# Verificar detección de infracciones
docker logs inference-service --tail 200 | grep "INFRACTION DETECTED"

# Si no hay resultados, habilitar simulación
simulate_infractions: true
```

---

### Problema: Líneas no detectadas (wrong_lane)

**Síntoma:**
```
🔍 Checking lane invasion: lane_detection=True, has_lanes={}
```

**Causas:**
1. ❌ Video sin líneas visibles
2. ❌ `lane_roi` mal configurado
3. ❌ Líneas muy tenues o borrosas

**Solución:**
1. Usar video con líneas claras
2. Ajustar `lane_roi` para incluir zona con líneas
3. Verificar logs de detección de líneas:
```bash
docker logs inference-service --tail 100 | grep "Lanes detected"
```

---

### Problema: Placa no detectada

**Síntoma:**
```
⚠️ OCR failed for SPEED - Could not detect license plate
```

**Causas:**
1. ❌ Placa muy pequeña (<30px)
2. ❌ Baja resolución de video
3. ❌ Placa obscurecida/tapada
4. ❌ Motion blur excesivo

**Solución:**
1. Usar video con resolución mínima 720p
2. Placas deben ser visibles (40-60px mínimo)
3. Verificar que la placa esté en el frame
4. Revisar logs de OCR:
```bash
docker logs inference-service --tail 200 | grep -E "(OCR|Version|Raw text)"
```

---

## 📞 Comando de Debug Completo

```bash
# Ver todo el flujo de una infracción
docker logs inference-service --tail 500 | grep -E "(INFRACTION|OCR|PLATE|Version|Raw text|Valid plate|DUPLICATE)"
```

**Salida ejemplo:**
```
🚨 INFRACTION DETECTED: speed for car
🔤 Attempting OCR for SPEED infraction...
🖼️ Vehicle crop size: 200x130
🎨 Will try 3 image versions for OCR...
📊 Version 1 (resized): 3 text(s) detected
📊 Version 2 (CLAHE): 2 text(s) detected
📊 Version 3 (sharpened): 4 text(s) detected
🔤 Raw text: 'ABC123', conf: 0.78
✅ Valid plate format: ABC123
✅ PLATE DETECTED for SPEED: 'ABC-123' (confidence: 0.78)
✅ ✨ NEW UNIQUE INFRACTION REGISTERED: speed for plate 'ABC-123'
```
