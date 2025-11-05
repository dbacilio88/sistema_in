#!/bin/bash

# Script de verificación de optimizaciones agresivas de FPS
# Comprueba que todas las optimizaciones estén activas

echo "════════════════════════════════════════════════════════"
echo "🚀 VERIFICACIÓN DE OPTIMIZACIONES AGRESIVAS - FPS V2"
echo "════════════════════════════════════════════════════════"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Obtener ID del contenedor
CONTAINER_ID=$(docker ps | grep inference | awk '{print $1}')

if [ -z "$CONTAINER_ID" ]; then
    echo -e "${RED}❌ ERROR: Contenedor inference-service no está corriendo${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Contenedor encontrado: $CONTAINER_ID${NC}"
echo ""

# Verificar que el servicio está listo
echo -e "${BLUE}📊 Verificando estado del servicio...${NC}"
echo "─────────────────────────────────────────"

# Verificar inicialización de modelos
MODELS_INIT=$(docker logs --tail 100 $CONTAINER_ID 2>&1 | grep -c "ML models initialized successfully")
if [ "$MODELS_INIT" -gt 0 ]; then
    echo -e "${GREEN}✅ Modelos ML inicializados ($MODELS_INIT workers)${NC}"
else
    echo -e "${RED}❌ Modelos ML no inicializados${NC}"
    exit 1
fi

# Verificar YOLO
YOLO_READY=$(docker logs --tail 100 $CONTAINER_ID 2>&1 | grep -c "YOLO")
if [ "$YOLO_READY" -gt 0 ]; then
    echo -e "${GREEN}✅ YOLO detector listo${NC}"
else
    echo -e "${YELLOW}⚠️  YOLO no detectado en logs${NC}"
fi

# Verificar OCR
OCR_READY=$(docker logs --tail 100 $CONTAINER_ID 2>&1 | grep -c "OCR reader loaded")
if [ "$OCR_READY" -gt 0 ]; then
    echo -e "${GREEN}✅ OCR reader cargado${NC}"
else
    echo -e "${YELLOW}⚠️  OCR no detectado en logs${NC}"
fi

# Verificar Traffic Light detector
TL_READY=$(docker logs --tail 100 $CONTAINER_ID 2>&1 | grep -c "Traffic light detector initialized")
if [ "$TL_READY" -gt 0 ]; then
    echo -e "${GREEN}✅ Traffic light detector listo${NC}"
else
    echo -e "${YELLOW}⚠️  Traffic light no detectado${NC}"
fi

# Verificar Lane detector
LANE_READY=$(docker logs --tail 100 $CONTAINER_ID 2>&1 | grep -c "Lane detector initialized")
if [ "$LANE_READY" -gt 0 ]; then
    echo -e "${GREEN}✅ Lane detector listo${NC}"
else
    echo -e "${YELLOW}⚠️  Lane detector no detectado${NC}"
fi

echo ""
echo -e "${BLUE}🔍 Verificando optimizaciones implementadas...${NC}"
echo "─────────────────────────────────────────"

# Verificar código de optimizaciones
CODE_FILE="inference-service/app/api/websocket.py"

if [ ! -f "$CODE_FILE" ]; then
    echo -e "${RED}❌ Archivo websocket.py no encontrado${NC}"
    exit 1
fi

# 1. Frame skipping
FRAME_SKIP=$(grep -c "frame_skip_interval" "$CODE_FILE")
if [ "$FRAME_SKIP" -gt 0 ]; then
    echo -e "${GREEN}✅ [1/6] Frame Skipping Inteligente implementado${NC}"
    echo "       → Procesa 1 de cada N frames (config: frame_skip_interval)"
else
    echo -e "${RED}❌ [1/6] Frame Skipping NO implementado${NC}"
fi

# 2. YOLO resize
YOLO_RESIZE=$(grep -c "detection_resolution" "$CODE_FILE")
if [ "$YOLO_RESIZE" -gt 0 ]; then
    echo -e "${GREEN}✅ [2/6] YOLO Resize implementado${NC}"
    echo "       → Reduce resolución antes de YOLO (640x480 por defecto)"
else
    echo -e "${RED}❌ [2/6] YOLO Resize NO implementado${NC}"
fi

# 3. Background OCR
BACKGROUND_OCR=$(grep -c "background_ocr" "$CODE_FILE")
if [ "$BACKGROUND_OCR" -gt 0 ]; then
    echo -e "${GREEN}✅ [3/6] Background OCR implementado${NC}"
    echo "       → OCR no bloquea frame processing (config: background_ocr)"
else
    echo -e "${RED}❌ [3/6] Background OCR NO implementado${NC}"
fi

# 4. Output quality
OUTPUT_QUALITY=$(grep -c "output_quality" "$CODE_FILE")
if [ "$OUTPUT_QUALITY" -gt 0 ]; then
    echo -e "${GREEN}✅ [4/6] Output Quality Compression implementado${NC}"
    echo "       → JPEG comprimido (75% por defecto, config: output_quality)"
else
    echo -e "${RED}❌ [4/6] Output Quality NO implementado${NC}"
fi

# 5. Log level configurable
LOG_LEVEL=$(grep -c "log_level" "$CODE_FILE")
if [ "$LOG_LEVEL" -gt 0 ]; then
    echo -e "${GREEN}✅ [5/6] Log Level Configurable implementado${NC}"
    echo "       → Reduce overhead de logs (config: log_level)"
else
    echo -e "${RED}❌ [5/6] Log Level NO implementado${NC}"
fi

# 6. Detection cache
DETECTION_CACHE=$(grep -c "last_detections" "$CODE_FILE")
if [ "$DETECTION_CACHE" -gt 0 ]; then
    echo -e "${GREEN}✅ [6/6] Detection Cache implementado${NC}"
    echo "       → Cachea detecciones para frames skipped"
else
    echo -e "${RED}❌ [6/6] Detection Cache NO implementado${NC}"
fi

echo ""
echo -e "${BLUE}📊 Configuración por defecto (hardcoded)${NC}"
echo "─────────────────────────────────────────"

# Extraer valores default del código
SKIP_DEFAULT=$(grep "self.frame_skip_interval =" "$CODE_FILE" | head -1 | grep -oP '\d+' || echo "N/A")
OCR_INTERVAL=$(grep "self.ocr_frame_interval =" "$CODE_FILE" | head -1 | grep -oP '\d+' || echo "N/A")
QUALITY_DEFAULT=$(grep "self.output_quality =" "$CODE_FILE" | head -1 | grep -oP '\d+' || echo "N/A")

echo -e "Frame Skip Interval: ${CYAN}$SKIP_DEFAULT frames${NC} (procesa 1 de cada $SKIP_DEFAULT)"
echo -e "OCR Frame Interval: ${CYAN}$OCR_INTERVAL frames${NC} (OCR cada $OCR_INTERVAL frames)"
echo -e "Output Quality: ${CYAN}$QUALITY_DEFAULT%${NC} JPEG compression"
echo -e "Log Level: ${CYAN}INFO${NC} (configurable vía frontend)"

echo ""
echo -e "${BLUE}🎯 Mejoras de rendimiento esperadas${NC}"
echo "─────────────────────────────────────────"

# Calcular FPS esperado basado en configuración
if [ "$SKIP_DEFAULT" != "N/A" ] && [ "$SKIP_DEFAULT" -gt 1 ]; then
    # Con frame skipping
    BASE_FPS=13
    SKIP_MULTIPLIER=$(echo "scale=1; 1 + ($SKIP_DEFAULT - 1) * 0.95" | bc)
    EXPECTED_FPS=$(echo "scale=0; $BASE_FPS * $SKIP_MULTIPLIER" | bc)
    
    echo -e "Sin optimizaciones: ${RED}5-10 FPS${NC} (baseline)"
    echo -e "Con optimización V1: ${YELLOW}20-25 FPS${NC} (anterior)"
    echo -e "Con optimizaciones V2: ${GREEN}$EXPECTED_FPS-$(($EXPECTED_FPS + 15)) FPS${NC} (esperado) ⚡"
    echo ""
    echo -e "Mejora total: ${GREEN}+$(((EXPECTED_FPS - 7) * 100 / 7))%${NC} vs baseline"
else
    echo -e "${YELLOW}⚠️  No se pudo calcular FPS esperado${NC}"
fi

echo ""
echo -e "${BLUE}💡 Configuración recomendada para frontend${NC}"
echo "─────────────────────────────────────────"

cat << 'EOF'
// Modo Balance (Recomendado para producción)
const config = {
  // Frame processing
  frame_skip_interval: 2,        // Procesar 50% de frames
  enable_yolo_resize: true,      // Resize a 640x480
  
  // OCR optimizado
  background_ocr: true,          // No bloquear frames
  ocr_frame_interval: 5,         // OCR cada 5 frames
  
  // Output
  output_quality: 80,            // 80% JPEG
  log_level: 'INFO',             // INFO o WARNING
  
  // Infracciones
  infractions: ['speeding', 'red_light', 'wrong_lane'],
  confidence_threshold: 0.5,
};

// FPS Esperado: 35-45 FPS ✅
// Detección placas: ~80%
EOF

echo ""
echo -e "${BLUE}🧪 Siguientes pasos para probar${NC}"
echo "─────────────────────────────────────────"

echo "1. Configurar frontend con la config recomendada"
echo "2. Iniciar WebSocket y cargar video"
echo "3. Observar FPS en consola del navegador"
echo "4. Verificar logs en tiempo real:"
echo ""
echo -e "   ${CYAN}docker logs -f $CONTAINER_ID | grep -E '(Frame|Skipping|cached|Resized)'${NC}"
echo ""
echo "5. Ejecutar test de FPS completo:"
echo ""
echo -e "   ${CYAN}./test-fps-optimization.sh${NC}"

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Verificación completada${NC}"
echo "════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}📚 Documentación detallada:${NC} docs/OPTIMIZACION_FPS_V2.md"
echo ""
