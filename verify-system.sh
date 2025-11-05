#!/bin/bash
# Script de verificación completa del sistema de infracciones

echo "🔍 VERIFICACIÓN COMPLETA DEL SISTEMA"
echo "====================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar Inference Service
echo "1️⃣  Verificando Inference Service (Docker)..."
if docker ps | grep -q traffic-inference; then
    echo -e "${GREEN}✅ Inference service está corriendo${NC}"
else
    echo -e "${RED}❌ Inference service NO está corriendo${NC}"
    echo "   Ejecutar: docker start traffic-inference"
fi
echo ""

# 2. Verificar Django Backend
echo "2️⃣  Verificando Django Backend (Puerto 8000)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/infractions/ | grep -q "200"; then
    echo -e "${GREEN}✅ Django backend respondiendo correctamente${NC}"
else
    echo -e "${RED}❌ Django backend NO responde${NC}"
    echo "   Verificar: ps aux | grep 'manage.py runserver'"
fi
echo ""

# 3. Verificar PostgreSQL
echo "3️⃣  Verificando PostgreSQL (Docker)..."
if docker ps | grep -q traffic-postgres; then
    echo -e "${GREEN}✅ PostgreSQL está corriendo${NC}"
    
    # Contar infracciones
    TOTAL=$(docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "SELECT COUNT(*) FROM infractions_infraction;" -t 2>/dev/null | tr -d ' \r\n')
    echo "   📊 Total de infracciones en BD: $TOTAL"
else
    echo -e "${RED}❌ PostgreSQL NO está corriendo${NC}"
    echo "   Ejecutar: docker start traffic-postgres"
fi
echo ""

# 4. Verificar logs recientes
echo "4️⃣  Verificando logs recientes (últimos 10 segundos)..."
RECENT_LOGS=$(docker logs --since 10s traffic-inference 2>&1 | wc -l)
if [ "$RECENT_LOGS" -gt 0 ]; then
    echo -e "${GREEN}✅ Servicio activo (${RECENT_LOGS} líneas de log)${NC}"
else
    echo -e "${YELLOW}⚠️  No hay logs recientes (servicio inactivo o sin actividad)${NC}"
fi
echo ""

# 5. Verificar clases detectables
echo "5️⃣  Verificando configuración de detección..."
echo "   Clases ahora detectables:"
echo "   - 0: person (👤 personas)"
echo "   - 1: bicycle (🚲 bicicletas)"
echo "   - 2: car (🚗 autos)"
echo "   - 3: motorcycle (🏍️ motos)"
echo "   - 5: bus (🚌 buses)"
echo "   - 7: truck (🚚 camiones)"
echo ""

# 6. Últimas infracciones
echo "6️⃣  Últimas 5 infracciones registradas:"
echo "----------------------------------------"
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    infraction_code as codigo,
    ROUND(detected_speed::numeric, 1) || ' km/h' as velocidad,
    COALESCE(NULLIF(license_plate_detected, ''), 'SIN PLACA') as placa,
    TO_CHAR(detected_at, 'YYYY-MM-DD HH24:MI:SS') as fecha
FROM infractions_infraction 
ORDER BY detected_at DESC 
LIMIT 5;
" 2>/dev/null
echo ""

# 7. Resumen
echo "📊 RESUMEN"
echo "========="
echo ""

# Estado general
INFERENCE_OK=$(docker ps | grep -q traffic-inference && echo "1" || echo "0")
DJANGO_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/infractions/ | grep -q "200" && echo "1" || echo "0")
POSTGRES_OK=$(docker ps | grep -q traffic-postgres && echo "1" || echo "0")

TOTAL_OK=$((INFERENCE_OK + DJANGO_OK + POSTGRES_OK))

if [ "$TOTAL_OK" -eq 3 ]; then
    echo -e "${GREEN}✅ TODOS LOS SERVICIOS FUNCIONANDO CORRECTAMENTE${NC}"
    echo ""
    echo "🎬 ¡Listo para probar con video!"
    echo ""
    echo "📋 Configuración recomendada:"
    echo "{"
    echo '  "simulate_infractions": true,'
    echo '  "infractions": ["speeding"],'
    echo '  "speed_limit": 60,'
    echo '  "confidence_threshold": 0.5,'
    echo '  "enable_ocr": false'
    echo "}"
elif [ "$TOTAL_OK" -eq 2 ]; then
    echo -e "${YELLOW}⚠️  ALGUNOS SERVICIOS CON PROBLEMAS${NC}"
    echo "   Revisar los mensajes arriba para detalles"
else
    echo -e "${RED}❌ SISTEMA NO ESTÁ FUNCIONANDO${NC}"
    echo "   Revisar todos los servicios"
fi

echo ""
echo "🔧 Comandos útiles:"
echo "   Ver logs en vivo: docker logs -f traffic-inference"
echo "   Reiniciar inference: docker restart traffic-inference"
echo "   Ver BD: psql -U postgres -d traffic_system"
echo ""
echo "📖 Documentación:"
echo "   docs/SOLUCION_DETECCION_PERSONAS.md"
echo "   docs/PRUEBA_VIDEO_INFRACCIONES.md"
echo "   docs/GUIA_RAPIDA_INFRACCIONES.md"
echo ""
