#!/bin/bash

# 🔍 Script para verificar la conexión con la base de datos y el guardado de infracciones

echo "======================================"
echo "🔍 VERIFICACIÓN DE SISTEMA"
echo "======================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar servicios corriendo
echo "1️⃣ Verificando servicios..."
echo ""

# Backend Django
if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend Django corriendo (puerto 8000)${NC}"
else
    echo -e "${RED}❌ Backend Django NO responde en puerto 8000${NC}"
    echo "   Iniciar con: cd backend-django && python manage.py runserver"
fi

# Inference Service
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Inference Service corriendo (puerto 8001)${NC}"
else
    echo -e "${RED}❌ Inference Service NO responde en puerto 8001${NC}"
    echo "   Iniciar con: cd inference-service && uvicorn app.main:app --reload --port 8001"
fi

# Base de datos PostgreSQL
if docker ps | grep -q postgres; then
    echo -e "${GREEN}✅ PostgreSQL corriendo (Docker)${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL no encontrado en Docker${NC}"
    echo "   Verificar con: docker ps | grep postgres"
fi

echo ""
echo "======================================"
echo "2️⃣ Probando API de infracciones..."
echo "======================================"
echo ""

# Test 1: Crear infracción de velocidad
echo "📝 Test 1: Crear infracción de VELOCIDAD..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/infractions/ \
  -H "Content-Type: application/json" \
  -d '{
    "infraction_type": "speed",
    "detected_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
    "severity": "high",
    "status": "pending",
    "license_plate_detected": "TEST-001",
    "license_plate_confidence": 0.95,
    "detected_speed": 120.0,
    "speed_limit": 60,
    "evidence_metadata": {
      "vehicle_type": "car",
      "confidence": 0.92,
      "source": "test_script"
    }
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Infracción de velocidad creada exitosamente${NC}"
    INFRACTION_CODE=$(echo "$BODY" | grep -o '"infraction_code":"[^"]*"' | cut -d'"' -f4)
    echo "   Código: $INFRACTION_CODE"
else
    echo -e "${RED}❌ Error al crear infracción (HTTP $HTTP_CODE)${NC}"
    echo "   Response: $BODY"
fi

echo ""

# Test 2: Crear infracción de semáforo en rojo
echo "📝 Test 2: Crear infracción de SEMÁFORO EN ROJO..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/infractions/ \
  -H "Content-Type: application/json" \
  -d '{
    "infraction_type": "red_light",
    "detected_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
    "severity": "high",
    "status": "pending",
    "license_plate_detected": "TEST-002",
    "license_plate_confidence": 0.88,
    "evidence_metadata": {
      "vehicle_type": "car",
      "confidence": 0.89,
      "traffic_light_state": "red",
      "stop_line_y": 400,
      "vehicle_position_y": 450,
      "source": "test_script"
    }
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Infracción de semáforo creada exitosamente${NC}"
    INFRACTION_CODE=$(echo "$BODY" | grep -o '"infraction_code":"[^"]*"' | cut -d'"' -f4)
    echo "   Código: $INFRACTION_CODE"
else
    echo -e "${RED}❌ Error al crear infracción (HTTP $HTTP_CODE)${NC}"
    echo "   Response: $BODY"
fi

echo ""

# Test 3: Crear infracción de invasión de carril
echo "📝 Test 3: Crear infracción de INVASIÓN DE CARRIL..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/infractions/ \
  -H "Content-Type: application/json" \
  -d '{
    "infraction_type": "wrong_lane",
    "detected_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
    "severity": "medium",
    "status": "pending",
    "license_plate_detected": "TEST-003",
    "license_plate_confidence": 0.91,
    "evidence_metadata": {
      "vehicle_type": "car",
      "confidence": 0.87,
      "subtype": "center_line_violation",
      "lane_crossed": "center",
      "distance": 25.5,
      "vehicle_position": [320, 240],
      "source": "test_script"
    }
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Infracción de carril creada exitosamente${NC}"
    INFRACTION_CODE=$(echo "$BODY" | grep -o '"infraction_code":"[^"]*"' | cut -d'"' -f4)
    echo "   Código: $INFRACTION_CODE"
else
    echo -e "${RED}❌ Error al crear infracción (HTTP $HTTP_CODE)${NC}"
    echo "   Response: $BODY"
fi

echo ""
echo "======================================"
echo "3️⃣ Verificando infracciones en BD..."
echo "======================================"
echo ""

# Contar infracciones
INFRACTION_COUNT=$(curl -s http://localhost:8000/api/infractions/ | grep -o '"id"' | wc -l)
echo "📊 Total de infracciones en BD: $INFRACTION_COUNT"

# Mostrar últimas 5 infracciones
echo ""
echo "📋 Últimas 5 infracciones:"
echo ""

INFRACTIONS=$(curl -s "http://localhost:8000/api/infractions/?limit=5&ordering=-detected_at")
echo "$INFRACTIONS" | python3 -m json.tool 2>/dev/null || echo "$INFRACTIONS"

echo ""
echo "======================================"
echo "4️⃣ Verificar base de datos PostgreSQL"
echo "======================================"
echo ""

# Verificar con psql si está disponible
if command -v docker &> /dev/null; then
    echo "🐘 Consultando PostgreSQL..."
    
    # Obtener nombre del contenedor de postgres
    POSTGRES_CONTAINER=$(docker ps --filter "ancestor=postgres" --format "{{.Names}}" | head -n1)
    
    if [ -n "$POSTGRES_CONTAINER" ]; then
        echo "   Container: $POSTGRES_CONTAINER"
        
        # Contar infracciones en la tabla
        COUNT=$(docker exec $POSTGRES_CONTAINER psql -U postgres -d traffic_db -t -c "SELECT COUNT(*) FROM infractions_infraction;" 2>/dev/null | tr -d ' ')
        
        if [ -n "$COUNT" ]; then
            echo -e "${GREEN}✅ Conexión a PostgreSQL exitosa${NC}"
            echo "   Total registros en tabla 'infractions_infraction': $COUNT"
            
            # Mostrar últimas infracciones
            echo ""
            echo "   Últimas 3 infracciones por tipo:"
            docker exec $POSTGRES_CONTAINER psql -U postgres -d traffic_db -c "
                SELECT 
                    infraction_code,
                    infraction_type,
                    severity,
                    license_plate_detected,
                    detected_at
                FROM infractions_infraction 
                ORDER BY detected_at DESC 
                LIMIT 3;
            " 2>/dev/null
        else
            echo -e "${YELLOW}⚠️  No se pudo consultar la base de datos${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No se encontró contenedor de PostgreSQL${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Docker no está disponible${NC}"
fi

echo ""
echo "======================================"
echo "✅ VERIFICACIÓN COMPLETA"
echo "======================================"
echo ""
echo "💡 Si hay errores:"
echo "   1. Verificar que los servicios estén corriendo"
echo "   2. Revisar logs: docker-compose logs -f"
echo "   3. Verificar migraciones: cd backend-django && python manage.py migrate"
echo "   4. Verificar configuración de BD en backend-django/config/settings.py"
echo ""
