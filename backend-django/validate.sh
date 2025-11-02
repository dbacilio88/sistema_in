#!/bin/bash
# Script completo de validación del proyecto Django

echo "=========================================="
echo "  VALIDACIÓN COMPLETA - DJANGO BACKEND"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

check_file() {
    if [ -f "$1" ]; then
        print_success "Archivo: $1"
        return 0
    else
        print_error "Falta archivo: $1"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        print_success "Directorio: $1/"
        return 0
    else
        print_error "Falta directorio: $1/"
        return 1
    fi
}

check_python_syntax() {
    if python3 -m py_compile "$1" 2>/dev/null; then
        return 0
    else
        print_error "Error de sintaxis en: $1"
        return 1
    fi
}

print_header "1. Verificando Estructura de Archivos"

# Core files
check_file "manage.py"
check_file "requirements.txt"
check_file "Dockerfile"
check_file "setup.cfg"
check_file "README.md"
check_file "verify_setup.sh"

echo ""
print_header "2. Verificando Package Config"

check_dir "config"
check_file "config/__init__.py"
check_file "config/settings.py"
check_file "config/urls.py"
check_file "config/wsgi.py"
check_file "config/asgi.py"
check_file "config/celery.py"
check_file "config/exceptions.py"

echo ""
print_header "3. Verificando App Authentication"

check_dir "authentication"
check_file "authentication/__init__.py"
check_file "authentication/apps.py"
check_file "authentication/models.py"
check_file "authentication/serializers.py"
check_file "authentication/views.py"
check_file "authentication/urls.py"
check_file "authentication/admin.py"
check_file "authentication/permissions.py"
check_file "authentication/utils.py"

check_dir "authentication/tests"
check_file "authentication/tests/__init__.py"
check_file "authentication/tests/test_models.py"
check_file "authentication/tests/test_api.py"

echo ""
print_header "4. Verificando Otras Apps"

for app in devices infractions vehicles; do
    check_dir "$app"
    check_file "$app/__init__.py"
    check_file "$app/apps.py"
    check_file "$app/models.py"
    check_file "$app/views.py"
    check_file "$app/urls.py"
    check_file "$app/admin.py"
done

echo ""
print_header "5. Verificando Sintaxis Python"

echo "Verificando archivos principales..."
python3 -m py_compile manage.py 2>/dev/null && print_success "manage.py - Sintaxis OK" || print_error "manage.py - Error de sintaxis"

for file in config/*.py; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        python3 -m py_compile "$file" 2>/dev/null && print_success "config/$filename - Sintaxis OK" || print_error "config/$filename - Error de sintaxis"
    fi
done

for file in authentication/*.py; do
    if [ -f "$file" ] && [[ "$file" != *"__pycache__"* ]]; then
        filename=$(basename "$file")
        python3 -m py_compile "$file" 2>/dev/null && print_success "authentication/$filename - Sintaxis OK" || print_error "authentication/$filename - Error de sintaxis"
    fi
done

echo ""
print_header "6. Contando Archivos y Líneas"

total_py=$(find . -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" -not -path "*/migrations/*" | wc -l)
total_lines=$(find . -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')

echo -e "${YELLOW}Total archivos Python:${NC} $total_py"
echo -e "${YELLOW}Total líneas de código:${NC} $total_lines"

echo ""
print_header "7. Verificando Dependencias en requirements.txt"

if [ -f "requirements.txt" ]; then
    total_deps=$(grep -c "^[a-zA-Z]" requirements.txt)
    echo -e "${YELLOW}Total dependencias:${NC} $total_deps"
    
    # Verificar dependencias críticas
    critical_deps=("Django==5.0.0" "djangorestframework==3.14.0" "djangorestframework-simplejwt" "psycopg2-binary" "celery" "redis" "pytest")
    
    for dep in "${critical_deps[@]}"; do
        if grep -q "$dep" requirements.txt; then
            print_success "Dependencia encontrada: $dep"
        else
            print_warning "Dependencia no encontrada: $dep"
        fi
    done
fi

echo ""
print_header "8. Verificando Configuración Docker"

if [ -f "Dockerfile" ]; then
    print_success "Dockerfile presente"
    
    # Verificar líneas clave en Dockerfile
    if grep -q "FROM python:3.11" Dockerfile; then
        print_success "Base image: Python 3.11"
    fi
    
    if grep -q "COPY requirements.txt" Dockerfile; then
        print_success "Copia requirements.txt"
    fi
    
    if grep -q "gunicorn" Dockerfile; then
        print_success "Configurado para Gunicorn"
    fi
fi

echo ""
print_header "9. Verificando Tests"

test_files=$(find authentication/tests -name "test_*.py" | wc -l)
echo -e "${YELLOW}Archivos de test encontrados:${NC} $test_files"

if [ -f "authentication/tests/test_models.py" ]; then
    test_count=$(grep -c "def test_" authentication/tests/test_models.py)
    echo -e "${YELLOW}Tests en test_models.py:${NC} $test_count"
fi

if [ -f "authentication/tests/test_api.py" ]; then
    test_count=$(grep -c "def test_" authentication/tests/test_api.py)
    echo -e "${YELLOW}Tests en test_api.py:${NC} $test_count"
fi

echo ""
print_header "10. Verificando Configuración en settings.py"

if [ -f "config/settings.py" ]; then
    # Verificar configuraciones importantes
    if grep -q "AUTH_USER_MODEL = 'authentication.User'" config/settings.py; then
        print_success "Custom User Model configurado"
    else
        print_warning "Custom User Model no encontrado"
    fi
    
    if grep -q "rest_framework_simplejwt" config/settings.py; then
        print_success "JWT authentication configurado"
    else
        print_warning "JWT authentication no encontrado"
    fi
    
    if grep -q "django.contrib.gis" config/settings.py; then
        print_success "PostGIS configurado"
    else
        print_warning "PostGIS no encontrado"
    fi
    
    if grep -q "CELERY_BROKER_URL" config/settings.py; then
        print_success "Celery configurado"
    else
        print_warning "Celery no encontrado"
    fi
fi

echo ""
print_header "11. Análisis de Modelos"

if [ -f "authentication/models.py" ]; then
    models_count=$(grep -c "^class.*models\\.Model" authentication/models.py)
    echo -e "${YELLOW}Modelos en authentication:${NC} $models_count"
    
    if grep -q "class User" authentication/models.py; then
        print_success "Modelo User definido"
    fi
    
    if grep -q "class LoginHistory" authentication/models.py; then
        print_success "Modelo LoginHistory definido"
    fi
fi

echo ""
print_header "12. Análisis de Endpoints"

if [ -f "authentication/urls.py" ]; then
    url_count=$(grep -c "path(" authentication/urls.py)
    echo -e "${YELLOW}URLs en authentication:${NC} $url_count"
fi

if [ -f "config/urls.py" ]; then
    if grep -q "/api/auth/" config/urls.py; then
        print_success "Endpoints de autenticación configurados"
    fi
    
    if grep -q "SpectacularSwaggerView" config/urls.py; then
        print_success "Swagger UI configurado"
    fi
    
    if grep -q "health" config/urls.py; then
        print_success "Health check endpoint configurado"
    fi
fi

echo ""
print_header "13. Resumen de Validación"

echo ""
echo "======================================"
echo "  RESULTADOS"
echo "======================================"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Sin errores críticos${NC}"
else
    echo -e "${RED}✗ $ERRORS errores encontrados${NC}"
fi

if [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ Sin advertencias${NC}"
else
    echo -e "${YELLOW}⚠ $WARNINGS advertencias${NC}"
fi

echo ""
echo "Archivos Python: $total_py"
echo "Líneas de código: $total_lines"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ VALIDACIÓN EXITOSA${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo "El proyecto Django está correctamente estructurado."
    echo ""
    echo "Próximos pasos:"
    echo "  1. Crear entorno virtual: python3 -m venv venv"
    echo "  2. Activar: source venv/bin/activate"
    echo "  3. Instalar deps: pip install -r requirements.txt"
    echo "  4. Configurar .env: cp ../.env.example ../.env"
    echo "  5. Ejecutar: python manage.py check"
    echo ""
    exit 0
else
    echo -e "${RED}════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ VALIDACIÓN FALLIDA${NC}"
    echo -e "${RED}════════════════════════════════════════${NC}"
    echo ""
    echo "Por favor, revisa los errores indicados arriba."
    echo ""
    exit 1
fi
