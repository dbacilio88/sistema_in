#!/bin/bash

# Script para iniciar el Dashboard Frontend
# Debe ejecutarse desde el directorio frontend-dashboard/

echo "🚀 Iniciando Dashboard de Monitoreo de Tráfico..."
echo "📍 Ubicación: frontend-dashboard/"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json"
    echo "   Asegúrate de ejecutar este script desde el directorio frontend-dashboard/"
    exit 1
fi

# Verificar dependencias
echo "📦 Verificando dependencias..."
if [ ! -d "node_modules" ]; then
    echo "📥 Instalando dependencias..."
    npm install
fi

# Iniciar el servidor de desarrollo
echo ""
echo "🌐 Iniciando servidor de desarrollo..."
echo "📱 El dashboard estará disponible en: http://localhost:3000"
echo "🔧 Modo: Desarrollo con hot-reload"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"
echo ""

npm run dev