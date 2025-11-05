#!/bin/bash

# Script para monitorear infracciones de wrong_lane y detección de placas
# Muestra logs en tiempo real del contenedor

echo "🔍 =================================================="
echo "🔍 MONITORING WRONG_LANE INFRACTIONS + OCR"
echo "🔍 =================================================="
echo ""
echo "Watching Docker logs for wrong_lane detection..."
echo "Press Ctrl+C to stop"
echo ""

# Seguir los logs del contenedor filtrando por información relevante
docker logs -f 83bc8d718fc7 2>&1 | grep -E \
    --line-buffered \
    --color=always \
    '(wrong_lane|INFRACTION FROM FRONTEND|INFRACTION DETECTED|Attempting OCR|PLATE DETECTED|B7J-482|B7J482|DUPLICATE|NEW UNIQUE|database save|SAVING INFRACTIONS)'
