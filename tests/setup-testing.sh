#!/bin/bash

# Script de setup para testing E2E
# Este script instala y configura Playwright para el proyecto

set -e

echo "🧪 Configurando Testing E2E con Playwright..."
echo ""

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Instalar Node.js 18+ antes de continuar."
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm no está instalado. Instalar npm antes de continuar."
    exit 1
fi

echo "📦 Instalando dependencias de testing..."
npm install

echo "🎭 Instalando navegadores de Playwright..."
npx playwright install

echo "🔧 Configurando archivos de entorno..."

# Crear archivo .env para tests
if [ ! -f ".env" ]; then
    cat > .env << EOL
# URLs para testing
BASE_URL=http://localhost:3000
DJANGO_URL=http://localhost:8000
FASTAPI_URL=http://localhost:8001

# Configuración de base de datos de test
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=traffic_system_test
TEST_DB_USER=postgres
TEST_DB_PASSWORD=postgres

# Configuración de Redis para tests
REDIS_URL=redis://localhost:6379/1

# Modo de testing
NODE_ENV=test
CI=false
HEADED=false
EOL
    echo "✅ Archivo .env creado"
else
    echo "ℹ️  Archivo .env ya existe"
fi

# Crear directorio para reportes
mkdir -p test-results
mkdir -p playwright-report

echo ""
echo "✅ Setup de testing E2E completado!"
echo ""
echo "📋 Comandos disponibles:"
echo "  npm test                 # Ejecutar todos los tests"
echo "  npm run test:headed      # Ejecutar tests con interfaz visual"
echo "  npm run test:debug       # Ejecutar tests en modo debug"
echo "  npm run test:ui          # Abrir interfaz de Playwright"
echo "  npm run test:report      # Ver reporte de la última ejecución"
echo ""
echo "🚀 Para ejecutar tests:"
echo "  1. Asegúrate de que los servicios estén corriendo:"
echo "     - Frontend: cd ../frontend-dashboard && npm run dev"
echo "     - Backend: cd ../backend-django && python manage.py runserver"
echo "     - API: cd ../inference-service && uvicorn app.main:app --port 8001"
echo "  2. Ejecuta: npm test"
echo ""