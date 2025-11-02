#!/bin/bash

echo "🔍 Verificación Rápida - Estado de ML"
echo "======================================"
echo ""

cd /home/bacsystem/github.com/sistema_in

# Verificar que el contenedor esté corriendo
STATUS=$(docker compose ps inference --format json 2>/dev/null | grep -o '"State":"[^"]*"' | cut -d'"' -f4)

if [ "$STATUS" = "running" ]; then
    echo "✅ Contenedor: Running"
else
    echo "❌ Contenedor: $STATUS"
    echo "   Ejecutar: docker compose up -d inference"
    exit 1
fi

echo ""
echo "📋 Últimos logs relevantes:"
echo "----------------------------"
docker compose logs inference --tail=20 | grep -E "(Initializing|YOLO|OCR|initialized|error|ERROR|warning|WARNING)" | tail -15

echo ""
echo "🎯 Verificación de Modelos:"
echo "----------------------------"

# Verificar YOLOv8
if docker compose logs inference | grep -q "YOLO model loaded"; then
    echo "✅ YOLOv8: Cargado correctamente"
else
    echo "❌ YOLOv8: No cargado"
fi

# Verificar OCR
if docker compose logs inference | grep -q "OCR reader loaded successfully"; then
    echo "✅ EasyOCR: Cargado correctamente"
elif docker compose logs inference | grep -q "Continuing without OCR support"; then
    echo "⚠️  EasyOCR: Deshabilitado (esto es OK por ahora)"
else
    echo "❌ EasyOCR: Estado desconocido"
fi

# Verificar inicialización general
if docker compose logs inference | grep -q "ML models initialized successfully"; then
    echo "✅ Sistema: Inicializado correctamente"
    echo ""
    echo "======================================"
    echo "🎉 SISTEMA LISTO PARA USAR"
    echo "======================================"
    echo ""
    echo "📱 Abrir en navegador:"
    echo "   http://localhost:3002"
    echo ""
    echo "🎥 Ir a: 'Monitoreo en Tiempo Real'"
    echo "   - Seleccionar 'Cámara Web Local'"
    echo "   - Deshabilitar OCR (no funciona aún)"
    echo "   - Click 'Iniciar Detección'"
    echo ""
    echo "🟢 Deberías ver:"
    echo "   - Cuadros VERDES en vehículos"
    echo "   - Tipo: car/truck/bus/motorcycle"
    echo "   - Confianza en %"
    echo ""
else
    echo "❌ Sistema: NO inicializado"
    echo ""
    echo "Ver errores completos:"
    echo "docker compose logs inference | grep -i error"
fi

echo ""

