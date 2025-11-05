# 🚀 Guía Rápida: OCR para Todas las Infracciones

## ✅ Sistema Listo

El sistema de detección de placas (OCR) ahora funciona **automáticamente** para **TODOS** los tipos de infracciones.

---

## 🎯 Tipos de Infracciones con OCR

| Tipo | Código | OCR |
|------|--------|-----|
| 🚗 Exceso de Velocidad | `speeding` | ✅ Automático |
| 🚦 Semáforo Rojo | `red_light` | ✅ Automático |
| 🛣️ Invasión de Carril | `wrong_lane` | ✅ Automático |
| 🪖 Sin Casco | `no_helmet` | ✅ Automático |
| 🔒 Sin Cinturón | `no_seatbelt` | ✅ Automático |

---

## 🚀 Inicio Rápido

### 1. Configuración Básica (Testing)

```typescript
// En LocalWebcamDetection.tsx
const detectionConfig = {
  infractions: ['speeding', 'wrong_lane', 'red_light'],
  confidence_threshold: 0.5,
  enable_speed: true,
  enable_lane_detection: true,
  speed_limit: 60,
  simulate_infractions: true, // ✅ Para pruebas rápidas
  ocr_all_vehicles: false
};
```

### 2. Iniciar Frontend

```bash
cd frontend-dashboard
npm run dev
```

### 3. Verificar Detecciones

```bash
# Ver placas detectadas
docker logs inference-service --tail 100 | grep "PLATE DETECTED"

# Resultado esperado:
✅ PLATE DETECTED for SPEED: 'ABC-123' (confidence: 0.78)
✅ PLATE DETECTED for RED_LIGHT: 'XYZ-789' (confidence: 0.71)
✅ PLATE DETECTED for WRONG_LANE: 'B7J-482' (confidence: 0.64)
```

---

## 📊 Verificación de Funcionamiento

### ✅ Verificar que el sistema está activo

```bash
docker ps | grep inference
```

**Resultado esperado:**
```
83bc8d718fc7   sistema_in-inference   Up 5 minutes (healthy)
```

### ✅ Verificar logs de OCR

```bash
docker logs inference-service --tail 200 | grep -E "(INFRACTION DETECTED|PLATE DETECTED)"
```

**Resultado esperado:**
```
🚨 INFRACTION DETECTED: speed for car
✅ PLATE DETECTED for SPEED: 'ABC-123' (confidence: 0.78)
🚨 INFRACTION DETECTED: red_light for car
✅ PLATE DETECTED for RED_LIGHT: 'XYZ-789' (confidence: 0.71)
```

### ✅ Verificar que no hay duplicados

```bash
docker logs inference-service --tail 200 | grep "DUPLICATE"
```

**Resultado esperado (cuando hay duplicados):**
```
⏭️ 🚫 DUPLICATE DETECTED: Plate 'ABC-123' already has speed infraction from 15 frames ago
```

---

## 🔧 Configuraciones por Escenario

### 🧪 Escenario 1: Testing Rápido (Simulación)

```json
{
  "infractions": ["speeding"],
  "confidence_threshold": 0.5,
  "enable_speed": true,
  "speed_limit": 60,
  "simulate_infractions": true
}
```

**Ventajas:**
- ✅ No requiere video especial
- ✅ Genera infracciones automáticamente
- ✅ Ideal para probar OCR

---

### 🏁 Escenario 2: Producción - Exceso de Velocidad

```json
{
  "infractions": ["speeding"],
  "confidence_threshold": 0.6,
  "enable_speed": true,
  "speed_limit": 60,
  "simulate_infractions": false
}
```

**Requisitos:**
- Video con vehículos en movimiento
- Sistema de tracking activo

---

### 🚦 Escenario 3: Producción - Semáforo Rojo

```json
{
  "infractions": ["red_light"],
  "confidence_threshold": 0.6,
  "stop_line_y": 450,
  "simulate_infractions": false
}
```

**Requisitos:**
- Video con semáforo visible
- Calibrar `stop_line_y` (coordenada Y de línea de parada)

**Calibración:**
1. Pausar video en línea de parada
2. Medir coordenada Y desde arriba
3. Configurar en frontend

---

### 🛣️ Escenario 4: Producción - Invasión de Carril

```json
{
  "infractions": ["wrong_lane"],
  "confidence_threshold": 0.6,
  "enable_lane_detection": true,
  "lane_roi": [[0, 480], [640, 480], [640, 200], [0, 200]],
  "simulate_infractions": false
}
```

**Requisitos:**
- ⚠️ **IMPORTANTE:** Video con líneas de carril VISIBLES (blancas/amarillas)
- Resolución mínima 720p
- Buena iluminación

**Problema Común:**
Si ves `has_lanes={}` → **No hay líneas detectadas**
- Solución: Usar video con líneas claras
- O ajustar `lane_roi` para incluir zona con líneas

---

### 🎯 Escenario 5: Todas las Infracciones

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

**Uso:** Testing completo de todos los tipos

---

## 📝 Formato de Placas Soportadas

El sistema acepta y normaliza automáticamente:

| Formato Original | Normalizado | Ejemplo |
|------------------|-------------|---------|
| ABC123 | ABC-123 | ABC-123 |
| ABC1234 | ABC-1234 | ABC-1234 |
| AB1234 | AB-1234 | AB-1234 |
| B7J482 | B7J-482 | B7J-482 |

**Requisitos:**
- 6-7 caracteres totales
- Combinación de letras y números
- Confianza mínima: 0.2

---

## ⚠️ Troubleshooting

### ❌ Problema: OCR no se ejecuta

**Síntoma:**
```
No aparecen logs de "Attempting OCR"
```

**Soluciones:**
1. Verificar que hay infracciones detectadas:
```bash
docker logs inference-service --tail 100 | grep "INFRACTION DETECTED"
```

2. Si no hay infracciones, habilitar simulación:
```json
{ "simulate_infractions": true }
```

---

### ❌ Problema: Líneas no detectadas (wrong_lane)

**Síntoma:**
```
🔍 Checking lane invasion: has_lanes={}
```

**Soluciones:**
1. Usar video con líneas de carril CLARAS (blancas/amarillas)
2. Verificar que `lane_roi` incluye zona con líneas
3. Ajustar parámetros de detección de líneas

**Verificar:**
```bash
docker logs inference-service --tail 100 | grep "Lanes detected"
```

**Salida esperada:**
```
🛣️ Lanes detected: 2 lanes (center: true)
```

---

### ❌ Problema: Placa no detectada

**Síntoma:**
```
⚠️ OCR failed for SPEED - Could not detect license plate
```

**Causas:**
1. Placa muy pequeña (<30px)
2. Video de baja resolución
3. Motion blur
4. Placa obscurecida

**Soluciones:**
1. Usar video con resolución mínima 720p
2. Verificar que placas sean visibles (40-60px)
3. Revisar logs detallados:
```bash
docker logs inference-service --tail 200 | grep -E "(OCR|Version|Raw text)"
```

---

## 📊 Ejemplo de Logs Exitosos

```bash
# Terminal de logs
docker logs -f inference-service
```

**Salida esperada:**

```
🚙 Processing vehicle #3: car
🎯 Real speed detection mode
🚨 SPEED VIOLATION: car at 85.2 km/h (limit: 60 km/h)
🚨 INFRACTION DETECTED: speed for car
   📍 Frame: 145, Vehicle Index: #3
   📦 BBox: [120, 50, 320, 180], Confidence: 0.87
   🎯 Infraction Type: speed
🔍 OCR Status: license_plate=None
🔤 Attempting OCR for SPEED infraction...
   📦 Vehicle bbox format: [120, 50, 320, 180]
   🎯 Infraction details: {'detected_speed': 85.2, 'speed_limit': 60}
📦 Converted bbox [x1,y1,x2,y2] to dict: {'x': 120, 'y': 50, 'width': 200, 'height': 130}
🖼️ Vehicle crop size: 200x130
🎨 Will try 3 image versions for OCR...
📊 Version 1 (resized): 3 text(s) detected
📊 Version 2 (CLAHE): 2 text(s) detected
📊 Version 3 (sharpened): 4 text(s) detected
🔤 Raw text: 'ABC123', conf: 0.78
🧹 Cleaned text: 'ABC123'
✅ Valid plate format: ABC123 (pattern: 3 letters + 3 numbers)
🔄 Normalized plate: ABC-123
✅ PLATE DETECTED for SPEED: 'ABC-123' (confidence: 0.78)
📊 Currently tracking 1 plates in cooldown:
   - 'ABC-123': speed (0 frames ago)
✅ ✨ NEW UNIQUE INFRACTION REGISTERED: speed for plate 'ABC-123' (frame 145). Will be saved to database.
```

---

## 📚 Documentación Completa

Para más detalles, consultar:

1. **`OCR_UNIVERSAL_INFRACCIONES.md`**
   - Descripción técnica completa
   - Flujo de detección
   - Proceso de OCR avanzado
   - Estadísticas de rendimiento

2. **`CONFIGURACION_OCR_INFRACCIONES.md`**
   - Configuraciones detalladas por escenario
   - Calibración de parámetros
   - Troubleshooting avanzado
   - Comandos de debug

3. **`RESUMEN_OCR_UNIVERSAL.md`**
   - Resumen ejecutivo
   - Cambios implementados
   - Tests realizados
   - Estado del sistema

---

## 🎉 Resumen

✅ **Sistema completamente funcional**
- OCR para TODAS las infracciones
- Validación inteligente
- Normalización automática
- Deduplicación activa
- Logs detallados

✅ **Listo para usar**
- Configuración simple
- Testing con simulación
- Producción con calibración

✅ **Documentación completa**
- Guías de uso
- Troubleshooting
- Ejemplos de configuración

---

**¿Necesitas ayuda?**
- Revisar logs: `docker logs inference-service --tail 200`
- Consultar documentación completa en `/docs`
- Verificar estado: `docker ps | grep inference`
