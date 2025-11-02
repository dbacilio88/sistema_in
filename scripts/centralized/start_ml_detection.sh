#!/bin/bash

echo "🚀 Iniciando Sistema de Detección ML"
echo "===================================="
echo ""

# Paso 1: Detener y limpiar contenedor anterior (si existe)
echo "🧹 Limpiando contenedor anterior..."
cd /home/bacsystem/github.com/sistema_in
docker compose stop inference 2>/dev/null
docker compose rm -f inference 2>/dev/null

# Paso 2: Reconstruir con permisos correctos
echo ""
echo "🔨 Reconstruyendo servicio (puede tardar 2-3 minutos)..."
docker compose build inference

# Paso 3: Iniciar inference
echo ""
echo "📦 Iniciando servicio de inferencia..."
docker compose up -d inference

echo ""
echo "⏳ Esperando a que los modelos se carguen (40 segundos)..."
echo "   (Primera vez descarga YOLOv8: ~6MB)"
sleep 40

# Verificar estado
echo ""
echo "✅ Verificando estado..."
docker compose ps inference

echo ""
echo "🔍 Buscando confirmación de modelos ML..."
docker compose logs inference | grep -E "(YOLO model loaded|OCR reader loaded|ML models initialized)" | tail -5

echo ""
echo "🔍 Buscando errores (si no aparece nada, está bien)..."
docker compose logs inference | grep -i "error" | tail -5

echo ""
echo "===================================="
echo "✅ SISTEMA LISTO"
echo "===================================="
echo ""
echo "📱 Abrir en el navegador:"
echo "   http://localhost:3002"
echo ""
echo "🎥 Pasos para usar:"
echo "   1. Ir a 'Monitoreo en Tiempo Real'"
echo "   2. Seleccionar 'Cámara Web Local'"
echo "   3. Click en 'Iniciar Detección'"
echo "   4. Permitir acceso a la cámara"
echo "   5. Esperar 5-10 segundos"
echo ""
echo "🟢 DEBERÍAS VER:"
echo "   - Cuadros verdes en vehículos detectados"
echo "   - Información de confianza y tipo"
echo "   - FPS en la esquina"
echo ""
echo "📋 Ver logs en tiempo real:"
echo "   docker compose logs -f inference"
echo ""
echo "🐛 Si no funciona, revisar:"
echo "   docs/TROUBLESHOOTING_ML.md"
echo ""

