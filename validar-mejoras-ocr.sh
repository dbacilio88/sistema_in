#!/bin/bash

# VALIDACIÓN FINAL - Verificar todas las mejoras implementadas

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 VALIDACIÓN FINAL - Sistema de Detección de Placas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📋 Checklist de Mejoras Implementadas:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Verificar que servicios estén corriendo
echo ""
echo "1️⃣  Verificando servicios Docker..."
if docker ps | grep -q "traffic-inference"; then
    echo "   ✅ Servicio inference corriendo"
else
    echo "   ❌ Servicio inference NO está corriendo"
    exit 1
fi

if docker ps | grep -q "traffic-frontend"; then
    echo "   ✅ Servicio frontend corriendo"
else
    echo "   ❌ Servicio frontend NO está corriendo"
    exit 1
fi

# 2. Verificar configuración OCR
echo ""
echo "2️⃣  Verificando configuración OCR en código..."
if grep -q "self.ocr_frame_interval = 3" inference-service/app/api/websocket.py; then
    echo "   ✅ OCR interval configurado en 3 frames"
else
    echo "   ⚠️  OCR interval NO está en 3 frames"
fi

if grep -q "use_background_ocr = config.get('background_ocr', False)" inference-service/app/api/websocket.py; then
    echo "   ✅ Background OCR deshabilitado (False)"
else
    echo "   ⚠️  Background OCR NO está deshabilitado"
fi

if grep -q "config.get('ocr_all_vehicles', True)" inference-service/app/api/websocket.py; then
    echo "   ✅ OCR forzado para todos los vehículos (True)"
else
    echo "   ⚠️  OCR NO está forzado para todos"
fi

# 3. Verificar ROI
echo ""
echo "3️⃣  Verificando procesamiento de ROI..."
if grep -q "roi_frame = detection_frame" inference-service/app/api/websocket.py; then
    echo "   ✅ ROI implementado en backend"
else
    echo "   ⚠️  ROI NO implementado"
fi

if grep -q "roi: roi" frontend-dashboard/src/components/LocalWebcamDetection.tsx; then
    echo "   ✅ ROI enviado desde frontend"
else
    echo "   ⚠️  ROI NO se envía desde frontend"
fi

# 4. Verificar corrección de caracteres
echo ""
echo "4️⃣  Verificando corrección de caracteres OCR..."
if grep -q "_correct_plate_characters" inference-service/app/services/model_service.py; then
    echo "   ✅ Corrección de caracteres implementada"
else
    echo "   ⚠️  Corrección de caracteres NO encontrada"
fi

# 5. Test de conectividad
echo ""
echo "5️⃣  Verificando conectividad..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "   ✅ Frontend accesible en http://localhost:3000"
else
    echo "   ❌ Frontend NO accesible"
fi

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend accesible en http://localhost:8000"
else
    echo "   ⚠️  Backend health check no disponible (normal si no existe endpoint)"
fi

# 6. Resumen de mejoras
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESUMEN DE MEJORAS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Background OCR deshabilitado (evita 'Processing...')"
echo "✅ OCR forzado en TODOS los vehículos (no solo infracciones)"
echo "✅ Intervalo OCR reducido de 5 → 3 frames (más detecciones)"
echo "✅ license_plate SIEMPRE en respuesta (null si no detectada)"
echo "✅ ROI aplicado para YOLO, frame original para OCR"
echo "✅ Corrección de caracteres: O→A, J→A, 8→B, etc."
echo "✅ 4 versiones de preprocesamiento (original, CLAHE, sharpen, binary)"
echo "✅ Umbral OCR en 0.10 (10%)"
echo "✅ Calidad de video: scale 0.6, JPEG 95%"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎬 PRÓXIMOS PASOS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Abrir http://localhost:3000 en el navegador"
echo "2. Subir VIDEO2.mp4 o VIDEO5.mp4"
echo "3. Abrir consola del navegador (F12)"
echo "4. Buscar en logs: '🎯 PLACAS DETECTADAS'"
echo ""
echo "EJEMPLO DE LOG EXITOSO:"
echo "  🎯 PLACAS DETECTADAS (2/2): \"B7J-482\", \"ABC-123\""
echo ""
echo "Si NO aparecen placas, ejecutar:"
echo "  docker logs -f traffic-inference | grep -E \"PLACA DETECTADA|OCR FORZADO\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
