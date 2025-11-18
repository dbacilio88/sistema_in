#!/bin/bash

echo "🔍 Verificación Canvas Rojo + OCR en Infracciones"
echo "================================================"
echo ""

echo "📱 FRONTEND - Dibujo de Detecciones:"
if grep -q "const boxColor = has_infraction ? '#FF0000' : '#00FF00'" frontend-dashboard/src/components/LocalWebcamDetection.tsx; then
    echo "  ✅ Canvas Rojo/Verde: IMPLEMENTADO"
else
    echo "  ❌ Canvas Rojo/Verde: NO IMPLEMENTADO"
fi

if grep -q "lastDetectionsRef.current = data.detections" frontend-dashboard/src/components/LocalWebcamDetection.tsx; then
    echo "  ✅ Actualización de Detecciones: IMPLEMENTADO"
else
    echo "  ❌ Actualización de Detecciones: NO IMPLEMENTADO"
fi

echo ""
echo "⚙️ BACKEND - OCR en Infracciones:"
if grep -q "self.ocr_frame_interval = 1" inference-service/app/api/websocket.py; then
    echo "  ✅ OCR en TODOS los frames: HABILITADO"
else
    echo "  ❌ OCR Interval: NO configurado correctamente"
fi

if grep -q "force_ocr_on_infraction = True" inference-service/app/api/websocket.py; then
    echo "  ✅ Force OCR on Infraction: HABILITADO"
else
    echo "  ❌ Force OCR on Infraction: NO HABILITADO"
fi

echo ""
echo "🐳 SERVICIOS:"
docker-compose ps frontend | grep -q "Up" && echo "  ✅ Frontend: Running" || echo "  ❌ Frontend: DOWN"
docker-compose ps inference | grep -q "Up" && echo "  ✅ Inference: Running" || echo "  ❌ Inference: DOWN"

echo ""
echo "🎯 PRUEBA AHORA:"
echo "1. http://localhost:3002"
echo "2. Subir VIDEO5.mp4"
echo "3. Activar OCR + Simulate Infractions"
echo "4. Speed Limit: 30 km/h"
echo ""
echo "✅ DEBERÍAS VER:"
echo "  • 🟢 Canvas VERDE en vehículos normales"
echo "  • 🔴 Canvas ROJO en vehículos con infracción"
echo "  • Labels: \"ABC-123 (73.8%)\""
echo "  • Console: Infraction con plate: \"ABC-123\""
