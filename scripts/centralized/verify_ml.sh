#!/bin/bash

echo "🔍 Verificando estado de modelos ML..."
echo "======================================"
echo ""

cd /home/bacsystem/github.com/sistema_in

echo "1. Estado del contenedor:"
docker compose ps inference | head -5

echo ""
echo "2. Últimos 30 logs:"
docker compose logs --tail=30 inference

echo ""
echo "3. Verificar inicialización exitosa:"
INIT_SUCCESS=$(docker compose logs inference | grep "ML models initialized successfully" | wc -l)
if [ $INIT_SUCCESS -gt 0 ]; then
    echo "✅ ML models initialized successfully"
else
    echo "❌ Modelos NO inicializados. Ver errores:"
    docker compose logs inference | grep -i error | tail -10
fi

echo ""
echo "4. Verificar archivos descargados:"
echo "   YOLOv8:"
docker exec traffic-inference ls -lh /app/models/ 2>/dev/null || echo "   ⚠️ No se pudo verificar"

echo "   EasyOCR:"
docker exec traffic-inference ls -lh /home/app/.EasyOCR/model/ 2>/dev/null | head -5 || echo "   ⚠️ No se pudo verificar"

echo ""
echo "======================================"
echo "Si todo está OK (✅), probar en:"
echo "http://localhost:3002 → Monitoreo en Tiempo Real"
echo ""

