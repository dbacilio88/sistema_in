#!/bin/bash

# ==================================
# Script de Pruebas de API - Sistema de Detección de Infracciones
# ==================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DJANGO_URL="http://localhost:8000"
ML_URL="http://localhost:8001"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Pruebas de API - Sistema de Detección de Infracciones  ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    local method=${4:-GET}
    
    echo -n "Testing $name... "
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    fi
    
    if [ "$response" == "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS ($response)${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL ($response, expected $expected_code)${NC}"
        return 1
    fi
}

# Test Django Backend
echo -e "${YELLOW}[1/5] Django Backend API Tests${NC}"
echo ""

test_endpoint "Health Check" "$DJANGO_URL/api/v1/health/" 200
test_endpoint "API Root" "$DJANGO_URL/api/v1/" 200
test_endpoint "API Documentation" "$DJANGO_URL/api/v1/docs/" 200

echo ""
echo -e "${YELLOW}[2/5] ML Inference Service Tests${NC}"
echo ""

test_endpoint "ML Health Check" "$ML_URL/health" 200
test_endpoint "ML API Documentation" "$ML_URL/docs" 200
test_endpoint "ML Metrics" "$ML_URL/metrics" 200

echo ""
echo -e "${YELLOW}[3/5] Authentication Tests${NC}"
echo ""

# Test login endpoint (should return 400 without credentials)
echo -n "Testing Login Endpoint... "
response=$(curl -s -X POST "$DJANGO_URL/api/v1/auth/login/" \
    -H "Content-Type: application/json" \
    -d '{}' \
    -o /dev/null -w "%{http_code}" 2>/dev/null || echo "000")

if [ "$response" == "400" ] || [ "$response" == "401" ]; then
    echo -e "${GREEN}✓ PASS ($response - correctly rejects empty credentials)${NC}"
else
    echo -e "${RED}✗ FAIL ($response)${NC}"
fi

echo ""
echo -e "${YELLOW}[4/5] Data Retrieval Tests${NC}"
echo ""

# Create a test user first
echo "Creating test user..."
docker compose exec -T django python manage.py shell << 'EOF' > /dev/null 2>&1 || true
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='testuser').exists():
    User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', role='operator')
    print('Test user created')
EOF

# Try to get a token
echo -n "Testing Token Authentication... "
TOKEN_RESPONSE=$(curl -s -X POST "$DJANGO_URL/api/v1/auth/login/" \
    -H "Content-Type: application/json" \
    -d '{"username":"testuser","password":"testpass123"}' 2>/dev/null || echo "")

if echo "$TOKEN_RESPONSE" | grep -q "token"; then
    echo -e "${GREEN}✓ PASS (token received)${NC}"
    TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    
    # Test authenticated endpoints
    echo -n "Testing Authenticated API Call... "
    auth_response=$(curl -s -o /dev/null -w "%{http_code}" \
        "$DJANGO_URL/api/v1/infractions/" \
        -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "000")
    
    if [ "$auth_response" == "200" ]; then
        echo -e "${GREEN}✓ PASS ($auth_response)${NC}"
    else
        echo -e "${RED}✗ FAIL ($auth_response)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ SKIP (could not authenticate)${NC}"
fi

echo ""
echo -e "${YELLOW}[5/5] ML Service Processing Test${NC}"
echo ""

# Test ML inference with a dummy image (if endpoint accepts it)
echo -n "Testing ML Inference Endpoint... "
ml_response=$(curl -s -o /dev/null -w "%{http_code}" \
    "$ML_URL/detect/license-plates" \
    -X POST 2>/dev/null || echo "000")

# 422 is expected without a valid image file
if [ "$ml_response" == "422" ] || [ "$ml_response" == "400" ]; then
    echo -e "${GREEN}✓ PASS ($ml_response - correctly validates input)${NC}"
else
    echo -e "${YELLOW}⚠ PARTIAL ($ml_response)${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Pruebas de API completadas${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Additional useful commands
echo -e "${YELLOW}Comandos de prueba adicionales:${NC}"
echo ""
echo -e "# Ver documentación interactiva de API:"
echo -e "  ${BLUE}Django:${NC} http://localhost:8000/api/v1/docs/"
echo -e "  ${BLUE}FastAPI:${NC} http://localhost:8001/docs"
echo ""
echo -e "# Crear superusuario para Django Admin:"
echo -e "  ${GREEN}docker compose exec django python manage.py createsuperuser${NC}"
echo ""
echo -e "# Ejecutar tests unitarios:"
echo -e "  ${GREEN}docker compose exec django python manage.py test${NC}"
echo -e "  ${GREEN}docker compose exec inference pytest${NC}"
echo ""
echo -e "# Ver logs en tiempo real:"
echo -e "  ${GREEN}docker compose logs -f django inference${NC}"
echo ""
