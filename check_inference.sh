#!/bin/bash

echo "=== Verificando estado del servicio de inferencia ==="
echo ""

echo "1. Estado del contenedor:"
docker compose ps inference

echo ""
echo "2. Últimos 30 logs:"
docker compose logs --tail=30 inference 2>&1 | tail -30

echo ""
echo "3. Buscar errores:"
docker compose logs --tail=100 inference 2>&1 | grep -i error | tail -10

echo ""
echo "4. Buscar inicialización de modelos:"
docker compose logs --tail=100 inference 2>&1 | grep -E "(Initializing|initialized|YOLO|OCR)" | tail -10

