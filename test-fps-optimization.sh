#!/bin/bash

# Script de prueba para verificar optimización de FPS
# Compara rendimiento con diferentes configuraciones de OCR

echo "════════════════════════════════════════════════════════"
echo "🚀 TEST DE OPTIMIZACIÓN DE FPS - Sistema OCR"
echo "════════════════════════════════════════════════════════"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que el contenedor está corriendo
echo -e "${BLUE}📊 Verificando estado del contenedor...${NC}"
CONTAINER_ID=$(docker ps | grep inference | awk '{print $1}')

if [ -z "$CONTAINER_ID" ]; then
    echo -e "${RED}❌ ERROR: Contenedor inference-service no está corriendo${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Contenedor encontrado: $CONTAINER_ID${NC}"
echo ""

# Función para contar logs de OCR en últimos N segundos
count_ocr_attempts() {
    local seconds=$1
    docker logs --since ${seconds}s $CONTAINER_ID 2>&1 | grep -c "Attempting OCR"
}

# Función para contar frames omitidos
count_skipped_frames() {
    local seconds=$1
    docker logs --since ${seconds}s $CONTAINER_ID 2>&1 | grep -c "Skipping OCR"
}

# Verificar configuración actual
echo -e "${BLUE}📋 Configuración Actual${NC}"
echo "─────────────────────────────────────────"

# Obtener intervalo de OCR de los últimos logs
OCR_INTERVAL=$(docker logs --tail 100 $CONTAINER_ID 2>&1 | grep "OCR interval" | tail -1 | grep -oP 'every \K[0-9]+' || echo "5")
echo -e "OCR Frame Interval: ${YELLOW}$OCR_INTERVAL frames${NC}"

# Verificar si verbose logging está activo
VERBOSE=$(docker logs --tail 100 $CONTAINER_ID 2>&1 | grep -c "Processing vehicle #" || echo "0")
if [ "$VERBOSE" -gt 0 ]; then
    echo -e "Verbose Logging: ${YELLOW}Activo${NC}"
else
    echo -e "Verbose Logging: ${GREEN}Desactivado (optimizado)${NC}"
fi

echo ""

# Esperar conexión de frontend
echo -e "${YELLOW}⏳ Esperando actividad del sistema...${NC}"
echo "Por favor, inicia el frontend y comienza a procesar video"
echo -e "${BLUE}Presiona ENTER cuando estés listo para comenzar el análisis...${NC}"
read

echo ""
echo -e "${BLUE}📊 Analizando rendimiento (30 segundos)...${NC}"
echo "─────────────────────────────────────────"

# Contar eventos antes
INFRACTIONS_BEFORE=$(docker logs --tail 500 $CONTAINER_ID 2>&1 | grep -c "INFRACTION DETECTED")
PLATES_BEFORE=$(docker logs --tail 500 $CONTAINER_ID 2>&1 | grep -c "PLATE DETECTED")

# Esperar 30 segundos recolectando datos
sleep 30

# Contar eventos después
INFRACTIONS_AFTER=$(docker logs --tail 500 $CONTAINER_ID 2>&1 | grep -c "INFRACTION DETECTED")
PLATES_AFTER=$(docker logs --tail 500 $CONTAINER_ID 2>&1 | grep -c "PLATE DETECTED")

# Calcular diferencias
INFRACTIONS_COUNT=$((INFRACTIONS_AFTER - INFRACTIONS_BEFORE))
PLATES_COUNT=$((PLATES_AFTER - PLATES_BEFORE))

# Obtener estadísticas de OCR
OCR_ATTEMPTS=$(count_ocr_attempts 30)
SKIPPED_FRAMES=$(count_skipped_frames 30)
TOTAL_FRAMES=$((OCR_ATTEMPTS + SKIPPED_FRAMES))

echo ""
echo -e "${GREEN}✅ Análisis Completado${NC}"
echo "════════════════════════════════════════════════════════"
echo ""

# Mostrar resultados
echo -e "${BLUE}📈 RESULTADOS (últimos 30 segundos)${NC}"
echo "─────────────────────────────────────────"
echo -e "Infracciones detectadas: ${YELLOW}$INFRACTIONS_COUNT${NC}"
echo -e "Placas detectadas: ${YELLOW}$PLATES_COUNT${NC}"
echo -e "Intentos de OCR: ${YELLOW}$OCR_ATTEMPTS${NC}"
echo -e "Frames omitidos (optimización): ${GREEN}$SKIPPED_FRAMES${NC}"

if [ "$TOTAL_FRAMES" -gt 0 ]; then
    SKIP_PERCENTAGE=$((SKIPPED_FRAMES * 100 / TOTAL_FRAMES))
    echo -e "Porcentaje de frames omitidos: ${GREEN}${SKIP_PERCENTAGE}%${NC}"
    echo ""
    
    # Calcular FPS estimado
    if [ "$OCR_INTERVAL" -gt 0 ]; then
        # FPS base (frames sin OCR): ~11 FPS
        # FPS con OCR: ~1.5 FPS
        FPS_WITHOUT_OCR=11
        FPS_WITH_OCR=1.5
        
        # Calcular FPS promedio según intervalo
        FRAMES_WITHOUT_OCR=$((OCR_INTERVAL - 1))
        AVG_FPS=$(echo "scale=1; ($FPS_WITHOUT_OCR * $FRAMES_WITHOUT_OCR + $FPS_WITH_OCR) / $OCR_INTERVAL" | bc)
        
        echo -e "${BLUE}🎯 FPS Estimado${NC}"
        echo "─────────────────────────────────────────"
        echo -e "Con intervalo $OCR_INTERVAL frames: ${GREEN}~${AVG_FPS} FPS${NC}"
        
        # Comparación con sin optimización
        echo -e "Sin optimización (interval=1): ${RED}~${FPS_WITH_OCR} FPS${NC}"
        
        # Calcular mejora
        IMPROVEMENT=$(echo "scale=0; ($AVG_FPS / $FPS_WITH_OCR * 100) - 100" | bc)
        echo -e "Mejora de rendimiento: ${GREEN}+${IMPROVEMENT}%${NC}"
    fi
fi

echo ""
echo -e "${BLUE}💡 Recomendaciones${NC}"
echo "─────────────────────────────────────────"

# Evaluar rendimiento y dar recomendaciones
if [ "$OCR_INTERVAL" -le 3 ]; then
    echo -e "${YELLOW}⚠️  Intervalo bajo detectado ($OCR_INTERVAL frames)${NC}"
    echo "   Para mejor FPS, considera aumentar a 5-7 frames"
    echo "   Comando: Configurar ocr_frame_interval: 5 en frontend"
elif [ "$OCR_INTERVAL" -ge 15 ]; then
    echo -e "${YELLOW}⚠️  Intervalo alto detectado ($OCR_INTERVAL frames)${NC}"
    echo "   Podrías perder detecciones de placas"
    echo "   Considera reducir a 7-10 frames para mejor balance"
else
    echo -e "${GREEN}✅ Intervalo óptimo ($OCR_INTERVAL frames)${NC}"
    echo "   Balance perfecto entre FPS y precisión"
fi

if [ "$VERBOSE" -gt 5 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Verbose logging activo${NC}"
    echo "   Configurar verbose_logging: false para +5-10% FPS"
fi

echo ""
echo -e "${BLUE}📊 Ver logs en tiempo real:${NC}"
echo "docker logs -f $CONTAINER_ID | grep -E '(INFRACTION|PLATE|Skipping OCR|OCR interval)'"

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Test completado${NC}"
echo "════════════════════════════════════════════════════════"
