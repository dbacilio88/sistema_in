#!/bin/bash

# Test WebSocket OCR - Verificar que el sistema detecta placas via WebSocket

echo "🔌 TEST WEBSOCKET OCR - Verificando detección de placas"
echo "=========================================================="
echo ""

# Monitorear logs del servicio de inferencia en tiempo real
echo "📡 Monitoreando logs del servicio de inferencia..."
echo "   Buscar: '✅ PLACA DETECTADA', 'OCR FORZADO', 'ROI recibido'"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

docker logs -f traffic-inference 2>&1 | grep --line-buffered -E "(PLACA DETECTADA|OCR FORZADO|ROI recibido|license_plate|NO se detectó placa|Ejecutando OCR)"
