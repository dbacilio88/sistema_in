#!/bin/bash

# 🚀 Script de instalación completa para el sistema de detección de infracciones
# Ejecutar desde la raíz del proyecto: ./install-backend.sh

echo "=========================================="
echo "🚀 INSTALACIÓN DE BACKEND DJANGO"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Cambiar al directorio backend-django
cd backend-django || {
    echo -e "${RED}❌ Error: No se encontró el directorio backend-django${NC}"
    echo "   Ejecuta este script desde la raíz del proyecto"
    exit 1
}

echo -e "${BLUE}📂 Directorio: $(pwd)${NC}"
echo ""

# Paso 1: Verificar Python
echo "1️⃣  Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python encontrado: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}❌ Python3 no está instalado${NC}"
    echo "   Instala Python 3.8 o superior"
    exit 1
fi
echo ""

# Paso 2: Verificar pip
echo "2️⃣  Verificando pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✅ pip encontrado: ${PIP_VERSION}${NC}"
else
    echo -e "${RED}❌ pip3 no está instalado${NC}"
    echo "   Instala con: sudo apt install python3-pip"
    exit 1
fi
echo ""

# Paso 3: Crear entorno virtual (opcional pero recomendado)
echo "3️⃣  Configurando entorno virtual..."
if [ ! -d "venv" ]; then
    echo "   Creando entorno virtual..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
else
    echo -e "${YELLOW}⚠️  Entorno virtual ya existe${NC}"
fi

# Activar entorno virtual
source venv/bin/activate 2>/dev/null || echo -e "${YELLOW}⚠️  No se pudo activar venv (continuando...)${NC}"
echo ""

# Paso 4: Actualizar pip
echo "4️⃣  Actualizando pip..."
python3 -m pip install --upgrade pip --quiet
echo -e "${GREEN}✅ pip actualizado${NC}"
echo ""

# Paso 5: Instalar dependencias
echo "5️⃣  Instalando dependencias (esto puede tomar varios minutos)..."
echo -e "${YELLOW}   Instalando desde requirements.txt...${NC}"

pip3 install -r requirements.txt --quiet --no-cache-dir

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
else
    echo -e "${RED}❌ Error al instalar dependencias${NC}"
    echo "   Intenta manualmente: pip3 install -r requirements.txt"
    exit 1
fi
echo ""

# Paso 6: Verificar instalación de paquetes clave
echo "6️⃣  Verificando paquetes clave..."
REQUIRED_PACKAGES=("django" "djangorestframework" "psycopg2" "environ")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "   ${GREEN}✅ $package${NC}"
    else
        echo -e "   ${RED}❌ $package${NC}"
    fi
done
echo ""

# Paso 7: Verificar PostgreSQL
echo "7️⃣  Verificando PostgreSQL..."
if docker ps | grep -q postgres; then
    echo -e "${GREEN}✅ PostgreSQL está corriendo${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL no está corriendo${NC}"
    echo "   Iniciando PostgreSQL..."
    cd ..
    docker-compose up -d postgres
    sleep 5
    cd backend-django
fi
echo ""

# Paso 8: Ejecutar migraciones
echo "8️⃣  Ejecutando migraciones..."
python3 manage.py migrate --noinput

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migraciones ejecutadas${NC}"
else
    echo -e "${RED}❌ Error en migraciones${NC}"
    echo "   Verifica la conexión a PostgreSQL"
fi
echo ""

# Paso 9: Inicializar base de datos
echo "9️⃣  Inicializando base de datos..."
python3 init_database.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Base de datos inicializada${NC}"
else
    echo -e "${YELLOW}⚠️  Advertencia: Algunos datos no se inicializaron${NC}"
fi
echo ""

# Paso 10: Verificar instalación
echo "🔟 Verificando instalación..."
python3 manage.py check --deploy 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Sistema verificado${NC}"
else
    echo -e "${YELLOW}⚠️  Hay algunas advertencias (esto es normal en desarrollo)${NC}"
fi
echo ""

echo "=========================================="
echo "✅ INSTALACIÓN COMPLETA"
echo "=========================================="
echo ""
echo "📊 Credenciales:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🚀 Para iniciar el servidor:"
echo "   cd backend-django"
echo "   source venv/bin/activate    # Activar entorno virtual"
echo "   python3 manage.py runserver"
echo ""
echo "🌐 URLs:"
echo "   API:   http://localhost:8000/api/"
echo "   Admin: http://localhost:8000/admin/"
echo "   Docs:  http://localhost:8000/api/schema/swagger/"
echo ""
echo "💡 Tip: Para desactivar el entorno virtual usa: deactivate"
echo ""
