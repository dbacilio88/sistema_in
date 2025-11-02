#!/bin/bash

# Esperar que PostgreSQL esté disponible
echo "Esperando que PostgreSQL esté disponible..."
python -c "
import psycopg2
import time
import os
while True:
    try:
        conn = psycopg2.connect(
            host='postgres',
            database=os.environ.get('DB_NAME', 'traffic_system'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres123!')
        )
        conn.close()
        break
    except:
        time.sleep(1)
"
echo "PostgreSQL está disponible"

# Ejecutar migraciones
echo "Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@traffic.local', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Cargar datos de prueba si la base está vacía
echo "Verificando y cargando datos de prueba..."
python manage.py shell -c "
from devices.models import Zone, Device
if not Zone.objects.exists():
    exec(open('seed_data.py').read())
    print('Datos de prueba cargados')
else:
    print('Datos de prueba ya existen')
"

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar el servidor
echo "Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000