#!/bin/bash
# Script de prueba para crear infracciones simuladas

echo "🧪 PRUEBA DE CREACIÓN DE INFRACCIONES"
echo "======================================"
echo ""

# Contar infracciones antes
BEFORE=$(docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction;" -t | tr -d ' \r\n')
echo "📊 Infracciones ANTES: $BEFORE"
echo ""

# Crear infracción de prueba SIN PLACA
echo "🚗 Creando infracción SIN PLACA..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "car",
        "confidence": 0.95,
        "bbox": [100, 100, 200, 200],
        "license_plate": "",
        "ocr_confidence": 0.0,
        "speed": 85.5,
        "infractions": ["speeding"]
      }
    ],
    "source": "test_script"
  }' | jq '.'
echo ""

# Crear infracción de prueba CON PLACA
echo "🚙 Creando infracción CON PLACA..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "car",
        "confidence": 0.92,
        "bbox": [300, 150, 450, 300],
        "license_plate": "TEST-999",
        "ocr_confidence": 0.88,
        "speed": 95.3,
        "infractions": ["speeding"]
      }
    ],
    "source": "test_script"
  }' | jq '.'
echo ""

# Crear infracción múltiple
echo "🚐 Creando múltiples infracciones..."
curl -s -X POST http://localhost:8000/api/infractions/from_detection/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "class_name": "truck",
        "confidence": 0.88,
        "bbox": [50, 50, 150, 150],
        "license_plate": "",
        "ocr_confidence": 0.0,
        "speed": 78.2,
        "infractions": ["speeding"]
      },
      {
        "class_name": "motorcycle",
        "confidence": 0.91,
        "bbox": [500, 200, 580, 320],
        "license_plate": "MOTO-123",
        "ocr_confidence": 0.75,
        "speed": 110.5,
        "infractions": ["speeding"]
      }
    ],
    "source": "test_script"
  }' | jq '.'
echo ""

# Esperar un momento
sleep 2

# Contar infracciones después
AFTER=$(docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction;" -t | tr -d ' \r\n')
echo "📊 Infracciones DESPUÉS: $AFTER"
echo "✅ Infracciones creadas: $((AFTER - BEFORE))"
echo ""

# Mostrar últimas infracciones
echo "📋 ÚLTIMAS 5 INFRACCIONES:"
echo "=========================="
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    infraction_code,
    infraction_type,
    detected_speed,
    CASE 
        WHEN license_plate_detected = '' OR license_plate_detected IS NULL 
        THEN 'SIN PLACA' 
        ELSE license_plate_detected 
    END as placa,
    status,
    TO_CHAR(detected_at, 'YYYY-MM-DD HH24:MI:SS') as fecha
FROM infractions_infraction 
ORDER BY detected_at DESC 
LIMIT 5;
"

echo ""
echo "📋 EVENTOS DE INFRACCIONES:"
echo "============================"
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    ie.event_type,
    i.infraction_code,
    CASE 
        WHEN i.license_plate_detected = '' OR i.license_plate_detected IS NULL 
        THEN 'SIN PLACA' 
        ELSE i.license_plate_detected 
    END as placa,
    TO_CHAR(ie.timestamp, 'YYYY-MM-DD HH24:MI:SS') as fecha
FROM infractions_infractionevent ie
JOIN infractions_infraction i ON ie.infraction_id = i.id
ORDER BY ie.timestamp DESC
LIMIT 5;
"

echo ""
echo "✅ PRUEBA COMPLETADA"
