#!/bin/bash

# Script de prueba para infracciones de invasión de carril
# Verifica la detección y almacenamiento de infracciones por cruce de líneas de carril

echo "🛣️ PRUEBA DE DETECCIÓN DE INVASIÓN DE CARRIL"
echo "============================================="
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
BEFORE=$(docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction WHERE infraction_type='wrong_lane';" -t | tr -d ' \r\n')
echo "📊 Infracciones de carril ANTES: $BEFORE"
echo ""

# Crear infracción por invasión de carril - Cruce de línea central
echo "🛣️ Creando infracción por CRUCE DE LÍNEA CENTRAL..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "car",
        "confidence": 0.91,
        "bbox": [200, 300, 350, 450],
        "license_plate": "LANE-001",
        "ocr_confidence": 0.87,
        "infractions": ["wrong_lane"]
      }
    ],
    "source": "test_script_lane",
    "metadata": {
      "subtype": "center_line_violation",
      "lane_crossed": "center",
      "distance": 15.5,
      "vehicle_position": [275, 375]
    }
  }' | jq '.'
echo ""

# Crear infracción por invasión de carril - Cruce de línea izquierda
echo "🚗 Creando infracción por CRUCE DE LÍNEA IZQUIERDA..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "truck",
        "confidence": 0.88,
        "bbox": [50, 250, 180, 400],
        "license_plate": "TRK-LEFT-99",
        "ocr_confidence": 0.82,
        "infractions": ["wrong_lane"]
      }
    ],
    "source": "test_script_lane",
    "metadata": {
      "subtype": "crossed_left_line",
      "lane_crossed": "left",
      "distance": 25.3,
      "vehicle_position": [115, 325]
    }
  }' | jq '.'
echo ""

# Crear infracción por invasión de carril - Cruce de línea derecha
echo "🚙 Creando infracción por CRUCE DE LÍNEA DERECHA..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "car",
        "confidence": 0.93,
        "bbox": [450, 280, 580, 420],
        "license_plate": "CAR-RIGHT-55",
        "ocr_confidence": 0.91,
        "infractions": ["wrong_lane"]
      }
    ],
    "source": "test_script_lane",
    "metadata": {
      "subtype": "crossed_right_line",
      "lane_crossed": "right",
      "distance": 18.7,
      "vehicle_position": [515, 350]
    }
  }' | jq '.'
echo ""

# Crear múltiples infracciones de carril
echo "🚐 Creando MÚLTIPLES infracciones de carril..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "bus",
        "confidence": 0.86,
        "bbox": [100, 200, 300, 400],
        "license_plate": "BUS-456",
        "ocr_confidence": 0.79,
        "infractions": ["wrong_lane"]
      },
      {
        "class_name": "motorcycle",
        "confidence": 0.94,
        "bbox": [350, 280, 420, 360],
        "license_plate": "MOTO-789",
        "ocr_confidence": 0.88,
        "infractions": ["wrong_lane"]
      }
    ],
    "source": "test_script_lane",
    "metadata": {
      "intersection": "Highway 101 - Lane 2",
      "road_type": "highway"
    }
  }' | jq '.'
echo ""

# Esperar un momento para que se procesen
sleep 2

# Contar infracciones después
AFTER=$(docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction WHERE infraction_type='wrong_lane';" -t | tr -d ' \r\n')
echo "📊 Infracciones de carril DESPUÉS: $AFTER"
echo "✅ Infracciones creadas: $((AFTER - BEFORE))"
echo ""

# Mostrar últimas infracciones de carril
echo "📋 ÚLTIMAS 5 INFRACCIONES DE CARRIL:"
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
  SELECT 
    infraction_code,
    infraction_type,
    severity,
    license_plate_detected,
    detected_at,
    status,
    evidence_metadata->>'subtype' as subtype,
    evidence_metadata->>'lane_crossed' as lane_crossed
  FROM infractions_infraction 
  WHERE infraction_type = 'wrong_lane'
  ORDER BY detected_at DESC 
  LIMIT 5;
" | head -n 25

echo ""
echo "✅ Prueba completada!"
echo ""
echo "💡 Verificaciones adicionales:"
echo "   - Revisa el dashboard en http://localhost:3000"
echo "   - Verifica logs del backend para ver el procesamiento"
echo "   - Las infracciones de línea central deberían tener severity='high'"
echo "   - Las infracciones de líneas laterales deberían tener severity='medium'"
