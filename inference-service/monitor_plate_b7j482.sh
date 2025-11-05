#!/bin/bash

# Script para monitorear la placa B7J-482 en los logs del contenedor
# Muestra logs filtrados para inspeccionar el proceso de detección y guardado

echo "🔍 =================================================="
echo "🔍 MONITORING PLATE B7J-482 DETECTION"
echo "🔍 =================================================="
echo ""
echo "Watching Docker logs for plate B7J-482..."
echo "Press Ctrl+C to stop"
echo ""

# Seguir los logs del contenedor filtrando por información relevante
docker logs -f 83bc8d718fc7 2>&1 | grep -E \
    --line-buffered \
    --color=always \
    '(B7J-482|B7J482|INFRACTION DETECTED|PLATE DETECTED|DUPLICATE|NEW UNIQUE|database save|Summary of saved|Code:)'
