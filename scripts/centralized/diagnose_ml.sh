#!/bin/bash

echo "==================================="
echo "DIAGNÓSTICO DE PROBLEMAS ML"
echo "==================================="
echo ""

echo "1. Estado de servicios críticos:"
echo "-----------------------------------"
docker compose ps inference minio frontend | head -10

echo ""
echo "2. Verificar si YOLO está cargado:"
echo "-----------------------------------"
docker compose logs inference 2>&1 | grep -E "(YOLO model loaded|Failed to load YOLO)" | tail -5

echo ""
echo "3. Verificar conexión WebSocket:"
echo "-----------------------------------"
docker compose logs inference 2>&1 | grep -i websocket | tail -5

echo ""
echo "4. Verificar MinIO (almacenamiento):"
echo "-----------------------------------"
echo "MinIO UI: http://localhost:9001"
echo "Buckets existentes:"
docker exec traffic-minio-client mc ls myminio/ 2>/dev/null || echo "No se pudo listar buckets"

echo ""
echo "5. Crear bucket para modelos ML:"
echo "-----------------------------------"
docker exec traffic-minio-client mc mb --ignore-existing myminio/ml-models 2>&1
docker exec traffic-minio-client mc policy set download myminio/ml-models 2>&1

echo ""
echo "6. Verificar archivo del modelo YOLO:"
echo "-----------------------------------"
docker exec traffic-inference ls -lh /app/models/ 2>/dev/null || echo "Contenedor inference no está corriendo"

echo ""
echo "==================================="
echo "RESUMEN:"
echo "==================================="
echo "- Si YOLO no está cargado: Esperar a que termine el rebuild"
echo "- Si no hay cuadros: Verificar que inference esté 'Up' y modelos cargados"
echo "- MinIO bucket 'ml-models' debería estar creado ahora"
echo ""

