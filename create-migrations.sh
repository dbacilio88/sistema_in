#!/bin/bash
# Script para crear migraciones y aplicarlas

echo "🔄 Creando migraciones para detecciones..."

# Ejecutar dentro del contenedor Django si existe
if docker ps | grep -q "traffic-django\|backend-django"; then
    echo "📦 Usando contenedor Docker..."
    docker exec -it $(docker ps | grep -E "traffic-django|backend-django" | awk '{print $1}') \
        python manage.py makemigrations infractions
    
    echo "📦 Aplicando migraciones..."
    docker exec -it $(docker ps | grep -E "traffic-django|backend-django" | awk '{print $1}') \
        python manage.py migrate infractions
else
    echo "⚠️  Contenedor Django no encontrado"
    echo "Intentando con el proceso local..."
    
    cd /home/bacsystem/github.com/sistema_in/backend-django
    
    # Buscar el Python correcto
    if [ -f "venv/bin/python" ]; then
        PYTHON="venv/bin/python"
    elif [ -f ".venv/bin/python" ]; then
        PYTHON=".venv/bin/python"
    else
        PYTHON="python3"
    fi
    
    echo "Usando: $PYTHON"
    
    $PYTHON manage.py makemigrations infractions
    $PYTHON manage.py migrate infractions
fi

echo "✅ Migraciones completadas"
