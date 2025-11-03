#!/bin/bash

# Script de inicio rápido para el servicio de inferencia
# Uso: ./start-inference-service.sh

echo "🚀 Iniciando servicio de inferencia..."
echo ""

# Directorio del servicio
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_DIR="$SCRIPT_DIR/inference-service"

# Verificar que el directorio existe
if [ ! -d "$SERVICE_DIR" ]; then
    echo "❌ Error: No se encuentra el directorio inference-service"
    exit 1
fi

cd "$SERVICE_DIR"

# Verificar que el entorno virtual existe
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "📦 No se encuentra entorno virtual. Creando uno nuevo..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Instalando dependencias..."
    pip install -r requirements.txt
else
    # Activar entorno virtual
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
fi

# Verificar que uvicorn está instalado
if ! command -v uvicorn &> /dev/null; then
    echo "📥 Instalando uvicorn..."
    pip install uvicorn
fi

echo ""
echo "✅ Iniciando servidor en http://localhost:8001"
echo "📝 Logs: inference-service.log"
echo "🛑 Detener: Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Iniciar servidor
python -m uvicorn app.main:app --reload --port 8001 --host 0.0.0.0 2>&1 | tee inference-service.log
