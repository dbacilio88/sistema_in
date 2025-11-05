#!/bin/bash

# 🚀 Script para inicializar la base de datos con migraciones y datos semilla

echo "=========================================="
echo "🗄️  INICIALIZACIÓN DE BASE DE DATOS"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Cambiar al directorio del script
cd "$(dirname "$0")/backend-django" || exit 1

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Error: No se encontró manage.py${NC}"
    echo "   Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

echo -e "${BLUE}📂 Directorio actual: $(pwd)${NC}"
echo ""

# Paso 1: Verificar PostgreSQL
echo "1️⃣  Verificando PostgreSQL..."
if docker ps | grep -q postgres; then
    echo -e "${GREEN}✅ PostgreSQL está corriendo${NC}"
else
    echo -e "${RED}❌ PostgreSQL no está corriendo${NC}"
    echo "   Iniciar con: docker-compose up -d postgres"
    exit 1
fi
echo ""

# Paso 2: Ejecutar migraciones
echo "2️⃣  Ejecutando migraciones..."
echo -e "${YELLOW}python manage.py migrate${NC}"
python manage.py migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migraciones ejecutadas exitosamente${NC}"
else
    echo -e "${RED}❌ Error al ejecutar migraciones${NC}"
    exit 1
fi
echo ""

# Paso 3: Crear superusuario (si no existe)
echo "3️⃣  Verificando superusuario..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@traffic.pe', 'admin123')
    print('✅ Superusuario creado: admin / admin123')
else:
    print('ℹ️  Superusuario ya existe')
EOF
echo ""

# Paso 4: Cargar datos semilla
echo "4️⃣  Cargando datos semilla..."
echo -e "${YELLOW}python seed_data.py${NC}"

if [ -f "seed_data.py" ]; then
    python seed_data.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Datos semilla cargados exitosamente${NC}"
    else
        echo -e "${YELLOW}⚠️  Algunos datos semilla ya existen (esto es normal)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No se encontró seed_data.py${NC}"
fi
echo ""

# Paso 5: Verificar datos en la base de datos
echo "5️⃣  Verificando datos en la base de datos..."
echo ""

python manage.py shell << 'EOF'
from infractions.models import Infraction
from devices.models import Device, Zone
from vehicles.models import Vehicle
from django.contrib.auth import get_user_model

User = get_user_model()

print(f"👥 Usuarios: {User.objects.count()}")
print(f"📍 Zonas: {Zone.objects.count()}")
print(f"📹 Dispositivos: {Device.objects.count()}")
print(f"🚗 Vehículos: {Vehicle.objects.count()}")
print(f"🚨 Infracciones: {Infraction.objects.count()}")
print("")

# Mostrar tipos de infracciones disponibles
from infractions.models import Infraction
print("📋 Tipos de infracción disponibles:")
print("   - speed (velocidad)")
print("   - red_light (semáforo en rojo)")
print("   - wrong_lane (invasión de carril)")
print("   - no_helmet (sin casco)")
print("   - parking (estacionamiento indebido)")
print("   - phone_use (uso de teléfono)")
print("   - seatbelt (sin cinturón)")
print("   - other (otros)")
EOF

echo ""
echo "=========================================="
echo "✅ INICIALIZACIÓN COMPLETA"
echo "=========================================="
echo ""
echo "📊 Credenciales de acceso:"
echo "   Admin:      admin / admin123"
echo "   Supervisor: supervisor / supervisor123"
echo "   Operator:   operator / operator123"
echo "   Auditor:    auditor / auditor123"
echo ""
echo "🌐 URLs:"
echo "   Backend API:  http://localhost:8000/api/"
echo "   Admin Panel:  http://localhost:8000/admin/"
echo "   Swagger:      http://localhost:8000/api/schema/swagger/"
echo ""
echo "🔧 Siguiente paso:"
echo "   Iniciar el servidor: python manage.py runserver"
echo ""
