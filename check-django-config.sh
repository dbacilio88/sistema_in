#!/bin/bash

# Script para verificar la configuración de Django en AWS

echo "🔍 Verificando configuración de Django en AWS..."

# Verificar variables de entorno
echo "📋 Variables de entorno ALLOWED_HOSTS:"
docker-compose -f docker-compose.yml -f docker-compose.aws.yml --env-file .env.aws exec django sh -c "echo \$ALLOWED_HOSTS"

# Verificar dentro del contenedor Django
echo "🐍 Verificando configuración Django desde Python:"
docker-compose -f docker-compose.yml -f docker-compose.aws.yml --env-file .env.aws exec django python manage.py shell -c "
from django.conf import settings
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
print('DEBUG:', settings.DEBUG)
print('CORS_ALLOWED_ORIGINS:', getattr(settings, 'CORS_ALLOWED_ORIGINS', 'Not set'))
"

# Verificar logs del contenedor
echo "📋 Últimos logs del contenedor Django:"
docker-compose -f docker-compose.yml -f docker-compose.aws.yml --env-file .env.aws logs --tail=20 django

echo "✅ Verificación completada"