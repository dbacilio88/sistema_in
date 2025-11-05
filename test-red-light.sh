#!/bin/bash

# Script de prueba para infracciones de semáforo en rojo
# Verifica la detección y almacenamiento de infracciones por luz roja

echo "🚦 PRUEBA DE DETECCIÓN DE SEMÁFORO EN ROJO"
echo "=========================================="
echo ""

# Verificar que el backend esté corriendo
echo "🔍 Verificando backend..."
curl -s http://localhost:8000/api/devices/ > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Backend no está corriendo en puerto 8000"
    echo "   Ejecuta: cd backend-django && python manage.py runserver"
    exit 1
fi
echo "✅ Backend corriendo"
echo ""

# Contar infracciones antes
BEFORE=$(docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction WHERE infraction_type='red_light';" -t | tr -d ' \r\n')
echo "📊 Infracciones de luz roja ANTES: $BEFORE"
echo ""

# Crear infracción por luz roja SIN PLACA
echo "🚦 Creando infracción de luz roja SIN PLACA..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "car",
        "confidence": 0.89,
        "bbox": [100, 50, 200, 150],
        "infractions": ["red_light"]
      }
    ],
    "source": "test_script_red_light",
    "metadata": {
      "traffic_light_state": "red",
      "stop_line_y": 400,
      "vehicle_position_y": 450
    }
  }' | jq '.'
echo ""

# Crear infracción por luz roja CON PLACA
echo "🚙 Creando infracción de luz roja CON PLACA..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "car",
        "confidence": 0.92,
        "bbox": [300, 150, 450, 300],
        "license_plate": "RED-LIGHT-001",
        "ocr_confidence": 0.88,
        "infractions": ["red_light"]
      }
    ],
    "source": "test_script_red_light",
    "metadata": {
      "traffic_light_state": "red",
      "stop_line_y": 400,
      "vehicle_position_y": 480
    }
  }' | jq '.'
echo ""

# Crear múltiples infracciones de luz roja
echo "🚐 Creando múltiples infracciones de luz roja..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "truck",
        "confidence": 0.85,
        "bbox": [50, 100, 150, 250],
        "license_plate": "TRK-789",
        "ocr_confidence": 0.82,
        "infractions": ["red_light"]
      },
      {
        "class_name": "motorcycle",
        "confidence": 0.91,
        "bbox": [200, 80, 280, 180],
        "license_plate": "MOT-456",
        "ocr_confidence": 0.85,
        "infractions": ["red_light"]
      }
    ],
    "source": "test_script_red_light",
    "metadata": {
      "traffic_light_state": "red",
      "stop_line_y": 350,
      "intersection": "Main St & 5th Ave"
    }
  }' | jq '.'
echo ""

# Esperar un momento para que se procesen
sleep 2

# Contar infracciones después
AFTER=$(docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction WHERE infraction_type='red_light';" -t | tr -d ' \r\n')
echo "📊 Infracciones de luz roja DESPUÉS: $AFTER"
echo "✅ Infracciones creadas: $((AFTER - BEFORE))"
echo ""

# Mostrar últimas infracciones de luz roja
echo "📋 ÚLTIMAS 5 INFRACCIONES DE LUZ ROJA:"
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
  SELECT 
    infraction_code,
    infraction_type,
    severity,
    license_plate_detected,
    detected_at,
    status
  FROM infractions_infraction 
  WHERE infraction_type = 'red_light'
  ORDER BY detected_at DESC 
  LIMIT 5;
" | head -n 20

echo ""
echo "✅ Prueba completada!"
echo ""
echo "💡 Verificaciones adicionales:"
echo "   - Revisa el dashboard en http://localhost:3000"
echo "   - Verifica logs del backend para ver el procesamiento"
echo "   - Verifica que las infracciones tengan severity='high'"
