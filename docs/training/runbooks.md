# Runbooks Operacionales - Sistema de Detección de Infracciones

## Introducción

Los runbooks operacionales proporcionan procedimientos paso a paso para operaciones críticas, mantenimiento rutinario y respuesta a incidentes. Están diseñados para ser ejecutados bajo presión y por personal con diferentes niveles de experiencia.

## 🚨 Procedimientos de Emergencia

### RB-001: Sistema Completamente Caído

#### Síntomas
- Interfaz web no responde
- APIs devuelven 503/504 errors
- Usuarios no pueden acceder al sistema

#### Tiempo Objetivo de Resolución
- **RTO**: 30 minutos
- **Escalamiento**: 15 minutos si no hay progreso

#### Procedimiento

**Paso 1: Verificación Inicial (2 minutos)**
```bash
# Verificar estado general del cluster
kubectl get nodes
kubectl get pods -A | grep -v Running

# Verificar ingress controller
kubectl get pods -n ingress-nginx
```

**Paso 2: Diagnóstico Rápido (5 minutos)**
```bash
# Verificar namespace principal
kubectl get pods -n traffic-system

# Verificar eventos recientes
kubectl get events -n traffic-system --sort-by='.lastTimestamp' | tail -20

# Verificar recursos
kubectl top nodes
kubectl get pvc -n traffic-system
```

**Paso 3: Acciones de Recuperación (10 minutos)**
```bash
# Si pods están CrashLoopBackOff
kubectl delete pod -l app.kubernetes.io/name=traffic-system -n traffic-system

# Si hay problemas de storage
kubectl get pvc -n traffic-system
kubectl describe pvc <problematic-pvc> -n traffic-system

# Si hay problemas de red
kubectl get svc -n traffic-system
kubectl describe ingress traffic-system -n traffic-system
```

**Paso 4: Escalamiento (si es necesario)**
```bash
# Activar modo de emergencia
kubectl scale deployment traffic-system-backend --replicas=10 -n traffic-system
kubectl scale deployment traffic-system-frontend --replicas=5 -n traffic-system

# Verificar auto-scaling
kubectl get hpa -n traffic-system
```

**Paso 5: Verificación de Recuperación (5 minutos)**
```bash
# Probar endpoints críticos
curl -f https://traffic-system.domain.com/health/
curl -f https://traffic-system.domain.com/api/v1/health/

# Verificar dashboard
# Acceder a Grafana y verificar métricas principales
```

**Comunicación:**
- Notificar a stakeholders inmediatamente
- Actualizar status page
- Documentar en incident ticket

---

### RB-002: Base de Datos Inaccesible

#### Síntomas
- Error "Database connection failed"
- 500 errors en API calls
- Timeouts en queries

#### Tiempo Objetivo de Resolución
- **RTO**: 20 minutos
- **Escalamiento**: 10 minutos si no hay progreso

#### Procedimiento

**Paso 1: Verificar Estado de PostgreSQL (2 minutos)**
```bash
# Verificar pods de PostgreSQL
kubectl get pods -l app.kubernetes.io/name=postgresql -n traffic-system

# Verificar logs
kubectl logs traffic-system-postgresql-0 -n traffic-system --tail=50
```

**Paso 2: Diagnóstico de Conectividad (3 minutos)**
```bash
# Probar conexión desde backend
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py dbshell

# Verificar service y endpoints
kubectl get svc traffic-system-postgresql -n traffic-system
kubectl get endpoints traffic-system-postgresql -n traffic-system
```

**Paso 3: Verificar Recursos (2 minutos)**
```bash
# Verificar uso de CPU/memoria
kubectl top pod traffic-system-postgresql-0 -n traffic-system

# Verificar storage
kubectl get pvc -l app.kubernetes.io/name=postgresql -n traffic-system
kubectl describe pvc <postgresql-pvc> -n traffic-system

# Verificar espacio en disco del nodo
kubectl get nodes -o wide
```

**Paso 4: Acciones de Recuperación (10 minutos)**

**Si PostgreSQL está caído:**
```bash
# Verificar configuración
kubectl describe pod traffic-system-postgresql-0 -n traffic-system

# Reiniciar PostgreSQL
kubectl delete pod traffic-system-postgresql-0 -n traffic-system

# Esperar que se recree
kubectl wait --for=condition=Ready pod/traffic-system-postgresql-0 -n traffic-system --timeout=300s
```

**Si hay problemas de performance:**
```bash
# Conectar a PostgreSQL
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
  psql -U trafficuser -d trafficdb

# Verificar conexiones activas
SELECT count(*) FROM pg_stat_activity;

# Verificar queries lentas
SELECT query, mean_time, calls FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

# Terminar conexiones si es necesario
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE state = 'active' AND query_start < now() - interval '5 minutes';
```

**Paso 5: Verificación (3 minutos)**
```bash
# Probar conectividad
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py check --database

# Verificar funcionamiento básico
curl -f https://traffic-system.domain.com/api/v1/infractions/ \
  -H "Authorization: Bearer <test-token>"
```

---

### RB-003: ML Service No Responde

#### Síntomas
- Timeouts en detección de placas
- Error 503 en endpoints ML
- Cola de procesamiento acumulándose

#### Tiempo Objetivo de Resolución
- **RTO**: 15 minutos
- **Escalamiento**: 8 minutos si no hay progreso

#### Procedimiento

**Paso 1: Verificar Estado del ML Service (2 minutos)**
```bash
# Verificar pods del ML service
kubectl get pods -l app.kubernetes.io/component=ml-service -n traffic-system

# Verificar logs recientes
kubectl logs deployment/traffic-system-ml-service -n traffic-system --tail=100
```

**Paso 2: Verificar Recursos GPU/CPU (3 minutos)**
```bash
# Verificar uso de recursos
kubectl top pod -l app.kubernetes.io/component=ml-service -n traffic-system

# Verificar GPU (si aplica)
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- nvidia-smi

# Verificar memoria de modelos
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
  du -sh /app/models/*
```

**Paso 3: Verificar Conectividad (2 minutos)**
```bash
# Probar endpoint de salud
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  curl -f http://traffic-system-ml-service:8001/health

# Verificar service
kubectl get svc traffic-system-ml-service -n traffic-system
kubectl describe svc traffic-system-ml-service -n traffic-system
```

**Paso 4: Acciones de Recuperación (6 minutos)**

**Si el servicio está sobrecargado:**
```bash
# Escalar horizontalmente
kubectl scale deployment traffic-system-ml-service --replicas=5 -n traffic-system

# Verificar auto-scaling
kubectl get hpa traffic-system-ml-service -n traffic-system
```

**Si hay problemas de memoria:**
```bash
# Aumentar límites de memoria temporalmente
kubectl patch deployment traffic-system-ml-service -n traffic-system -p='
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "ml-service",
          "resources": {
            "limits": {"memory": "8Gi"},
            "requests": {"memory": "4Gi"}
          }
        }]
      }
    }
  }
}'
```

**Si los modelos están corruptos:**
```bash
# Limpiar cache de modelos
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
  rm -rf /app/model_cache/*

# Reiniciar servicio para recargar modelos
kubectl rollout restart deployment/traffic-system-ml-service -n traffic-system
```

**Paso 5: Verificación (2 minutos)**
```bash
# Probar detección
curl -X POST http://ml-service:8001/detect/license-plates \
  -F "file=@test-image.jpg" \
  -F "confidence_threshold=0.8"

# Verificar métricas
curl http://ml-service:8001/metrics | grep -E "(request_duration|gpu_utilization)"
```

---

## 🔧 Procedimientos de Mantenimiento

### RB-101: Backup Completo del Sistema

#### Frecuencia
- **Diario**: Backup incremental
- **Semanal**: Backup completo
- **Mensual**: Backup con verificación de integridad

#### Procedimiento Completo (30 minutos)

**Paso 1: Preparación (5 minutos)**
```bash
# Crear directorio de backup
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/complete_$BACKUP_DATE"
mkdir -p $BACKUP_DIR

# Verificar espacio disponible
df -h /backups
```

**Paso 2: Backup de Base de Datos (10 minutos)**
```bash
# PostgreSQL dump
kubectl exec traffic-system-postgresql-0 -n traffic-system -- \
  pg_dump -U trafficuser -d trafficdb --verbose --clean --create | \
  gzip > $BACKUP_DIR/postgresql_$BACKUP_DATE.sql.gz

# Verificar integridad del archivo
gunzip -t $BACKUP_DIR/postgresql_$BACKUP_DATE.sql.gz
echo "PostgreSQL backup status: $?"
```

**Paso 3: Backup de Redis (3 minutos)**
```bash
# Forzar BGSAVE
kubectl exec traffic-system-redis-master-0 -n traffic-system -- \
  redis-cli BGSAVE

# Esperar completitud
kubectl exec traffic-system-redis-master-0 -n traffic-system -- \
  redis-cli LASTSAVE

# Copiar archivo RDB
kubectl cp traffic-system-redis-master-0:/data/dump.rdb \
  $BACKUP_DIR/redis_$BACKUP_DATE.rdb -n traffic-system
```

**Paso 4: Backup de MinIO (10 minutos)**
```bash
# Backup de todos los buckets
kubectl exec deployment/traffic-system-minio -n traffic-system -- \
  mc mirror --overwrite myminio/evidence $BACKUP_DIR/minio_evidence/

kubectl exec deployment/traffic-system-minio -n traffic-system -- \
  mc mirror --overwrite myminio/models $BACKUP_DIR/minio_models/

# Verificar integridad
find $BACKUP_DIR/minio_* -name "*.jpg" | wc -l
```

**Paso 5: Backup de Configuración (2 minutos)**
```bash
# Kubernetes configurations
kubectl get all,configmap,secret,pvc,ingress -n traffic-system -o yaml > \
  $BACKUP_DIR/kubernetes_config_$BACKUP_DATE.yaml

# Config service data
kubectl exec deployment/traffic-system-config-service -n traffic-system -- \
  tar -czf /tmp/config_backup.tar.gz /app/config/

kubectl cp traffic-system-config-service:/tmp/config_backup.tar.gz \
  $BACKUP_DIR/config_service_$BACKUP_DATE.tar.gz -n traffic-system
```

**Paso 6: Verificación y Almacenamiento**
```bash
# Crear manifest de backup
cat > $BACKUP_DIR/BACKUP_MANIFEST.txt << EOF
Backup Date: $BACKUP_DATE
System Version: $(kubectl get deployment traffic-system-backend -n traffic-system -o jsonpath='{.spec.template.spec.containers[0].image}')
PostgreSQL Size: $(ls -lh $BACKUP_DIR/postgresql_*.sql.gz | awk '{print $5}')
Redis Size: $(ls -lh $BACKUP_DIR/redis_*.rdb | awk '{print $5}')
MinIO Files: $(find $BACKUP_DIR/minio_* -type f | wc -l)
Config Size: $(ls -lh $BACKUP_DIR/config_*.tar.gz | awk '{print $5}')
Total Size: $(du -sh $BACKUP_DIR | awk '{print $1}')
EOF

# Subir a storage remoto
aws s3 sync $BACKUP_DIR s3://traffic-system-backups/complete/$BACKUP_DATE/

# Limpiar backups locales antiguos (mantener 7 días)
find /backups -name "complete_*" -mtime +7 -exec rm -rf {} \;
```

---

### RB-102: Actualización del Sistema

#### Frecuencia
- **Parches de seguridad**: Inmediato
- **Updates menores**: Mensual
- **Updates mayores**: Trimestral

#### Procedimiento de Actualización (45 minutos)

**Paso 1: Pre-actualización (10 minutos)**
```bash
# Backup completo del sistema
./runbook-101-backup.sh

# Verificar estado actual
kubectl get pods -n traffic-system
kubectl get events -n traffic-system --sort-by='.lastTimestamp' | tail -10

# Verificar recursos disponibles
kubectl top nodes
kubectl get pvc -n traffic-system
```

**Paso 2: Verificar Nuevas Versiones (5 minutos)**
```bash
# Actualizar repositorio Helm
helm repo update

# Verificar cambios
helm diff upgrade traffic-system ./helm \
  --namespace traffic-system \
  --values values-production.yaml

# Descargar nuevas imágenes
docker pull trafficsystem/backend:v1.2.0
docker pull trafficsystem/ml-service:v1.2.0
docker pull trafficsystem/config-service:v1.2.0
docker pull trafficsystem/frontend:v1.2.0
```

**Paso 3: Modo de Mantenimiento (2 minutos)**
```bash
# Activar página de mantenimiento
kubectl scale deployment traffic-system-frontend --replicas=0 -n traffic-system

# Desplegar página de mantenimiento
kubectl apply -f maintenance-page.yaml

# Notificar usuarios (actualizar status page)
curl -X POST https://status-page.com/api/incidents \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "Sistema en mantenimiento programado", "status": "maintenance"}'
```

**Paso 4: Actualización Gradual (25 minutos)**
```bash
# Actualizar backend (rolling update)
helm upgrade traffic-system ./helm \
  --namespace traffic-system \
  --values values-production.yaml \
  --set images.backend.tag=v1.2.0

# Verificar rollout del backend
kubectl rollout status deployment/traffic-system-backend -n traffic-system

# Actualizar ML service
helm upgrade traffic-system ./helm \
  --namespace traffic-system \
  --values values-production.yaml \
  --set images.mlService.tag=v1.2.0

# Verificar ML service
kubectl rollout status deployment/traffic-system-ml-service -n traffic-system

# Actualizar config service
helm upgrade traffic-system ./helm \
  --namespace traffic-system \
  --values values-production.yaml \
  --set images.configService.tag=v1.2.0

# Verificar config service
kubectl rollout status deployment/traffic-system-config-service -n traffic-system

# Actualizar frontend
helm upgrade traffic-system ./helm \
  --namespace traffic-system \
  --values values-production.yaml \
  --set images.frontend.tag=v1.2.0

# Verificar frontend
kubectl rollout status deployment/traffic-system-frontend -n traffic-system
```

**Paso 5: Verificación Post-actualización (3 minutos)**
```bash
# Verificar todos los pods
kubectl get pods -n traffic-system

# Probar endpoints críticos
curl -f https://traffic-system.domain.com/api/v1/health/
curl -f https://traffic-system.domain.com/api/v1/infractions/ \
  -H "Authorization: Bearer <test-token>"

# Probar ML service
curl -f http://ml-service:8001/health

# Verificar base de datos
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py check --database
```

**Paso 6: Finalización**
```bash
# Remover página de mantenimiento
kubectl delete -f maintenance-page.yaml

# Escalar frontend a producción
kubectl scale deployment traffic-system-frontend --replicas=3 -n traffic-system

# Actualizar status page
curl -X PATCH https://status-page.com/api/incidents/<incident-id> \
  -H "Authorization: Bearer <token>" \
  -d '{"status": "resolved", "message": "Mantenimiento completado exitosamente"}'

# Documentar en log de cambios
echo "$(date): Actualización exitosa a v1.2.0" >> /var/log/system-updates.log
```

---

### RB-103: Limpieza de Datos Antiguos

#### Frecuencia
- **Logs**: Diario
- **Archivos temporales**: Diario
- **Data archival**: Mensual

#### Procedimiento (20 minutos)

**Paso 1: Limpieza de Logs (5 minutos)**
```bash
# Logs de aplicación antiguos
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  find /app/logs -name "*.log" -mtime +30 -delete

kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
  find /app/logs -name "*.log" -mtime +30 -delete

# Logs de sistema
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  journalctl --vacuum-time=30d
```

**Paso 2: Archivos Temporales (3 minutos)**
```bash
# Archivos temporales del ML service
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
  find /tmp -name "*.jpg" -o -name "*.mp4" -mtime +1 -delete

# Cache de procesamiento
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
  find /app/cache -name "*" -mtime +7 -delete

# Uploads temporales
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  find /app/uploads/temp -name "*" -mtime +3 -delete
```

**Paso 3: Archival de Datos (10 minutos)**
```bash
# Conectar a base de datos
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
  psql -U trafficuser -d trafficdb

# Archivar infracciones antiguas (> 2 años)
BEGIN;

-- Crear tabla de archivo si no existe
CREATE TABLE IF NOT EXISTS infractions_archive (LIKE infractions INCLUDING ALL);

-- Mover datos antiguos
INSERT INTO infractions_archive 
SELECT * FROM infractions 
WHERE created_at < NOW() - INTERVAL '2 years';

-- Verificar datos movidos
SELECT COUNT(*) as archived_count FROM infractions_archive 
WHERE created_at >= NOW() - INTERVAL '1 day';

-- Si todo está bien, eliminar de tabla principal
DELETE FROM infractions 
WHERE created_at < NOW() - INTERVAL '2 years';

COMMIT;

-- Actualizar estadísticas
ANALYZE infractions;
ANALYZE infractions_archive;
```

**Paso 4: Limpieza de MinIO (2 minutos)**
```bash
# Listar objetos antiguos
kubectl exec deployment/traffic-system-minio -n traffic-system -- \
  mc find myminio/evidence --older-than 2y

# Mover a bucket de archivo
kubectl exec deployment/traffic-system-minio -n traffic-system -- \
  mc mirror myminio/evidence myminio/archive/evidence --older-than 2y

# Eliminar después de confirmar backup
# kubectl exec deployment/traffic-system-minio -n traffic-system -- \
#   mc rm --recursive --older-than 2y myminio/evidence
```

---

## 📊 Procedimientos de Monitoreo

### RB-201: Verificación de Salud del Sistema

#### Frecuencia
- **Automático**: Cada 5 minutos
- **Manual**: Diario (verificación visual)

#### Procedimiento Automatizado (5 minutos)

**Script de Verificación:**
```bash
#!/bin/bash
# health-check.sh

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
HEALTH_LOG="/var/log/health-checks.log"

echo "[$TIMESTAMP] Starting health check..." >> $HEALTH_LOG

# 1. Verificar pods críticos
CRITICAL_PODS=(
  "traffic-system-backend"
  "traffic-system-ml-service" 
  "traffic-system-config-service"
  "traffic-system-postgresql-0"
  "traffic-system-redis-master-0"
)

for pod in "${CRITICAL_PODS[@]}"; do
  STATUS=$(kubectl get pod $pod -n traffic-system -o jsonpath='{.status.phase}' 2>/dev/null)
  if [ "$STATUS" != "Running" ]; then
    echo "[$TIMESTAMP] ALERT: $pod is $STATUS" >> $HEALTH_LOG
    # Enviar alerta
    curl -X POST https://alertmanager:9093/api/v1/alerts \
      -H "Content-Type: application/json" \
      -d "[{\"labels\":{\"alertname\":\"PodNotRunning\",\"pod\":\"$pod\",\"severity\":\"critical\"}}]"
  else
    echo "[$TIMESTAMP] OK: $pod is running" >> $HEALTH_LOG
  fi
done

# 2. Verificar endpoints críticos
ENDPOINTS=(
  "https://traffic-system.domain.com/health/"
  "http://traffic-system-ml-service:8001/health"
  "http://traffic-system-config-service:8002/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" --max-time 10)
  if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "[$TIMESTAMP] OK: $endpoint responded with $HTTP_STATUS" >> $HEALTH_LOG
  else
    echo "[$TIMESTAMP] ALERT: $endpoint responded with $HTTP_STATUS" >> $HEALTH_LOG
    # Enviar alerta
    curl -X POST https://alertmanager:9093/api/v1/alerts \
      -H "Content-Type: application/json" \
      -d "[{\"labels\":{\"alertname\":\"EndpointDown\",\"endpoint\":\"$endpoint\",\"severity\":\"critical\"}}]"
  fi
done

# 3. Verificar uso de recursos
CPU_USAGE=$(kubectl top nodes --no-headers | awk '{print $3}' | sed 's/%//' | sort -nr | head -1)
if [ "$CPU_USAGE" -gt 80 ]; then
  echo "[$TIMESTAMP] WARNING: High CPU usage: $CPU_USAGE%" >> $HEALTH_LOG
fi

# 4. Verificar almacenamiento
STORAGE_USAGE=$(df /var/lib/docker | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$STORAGE_USAGE" -gt 85 ]; then
  echo "[$TIMESTAMP] WARNING: High storage usage: $STORAGE_USAGE%" >> $HEALTH_LOG
fi

echo "[$TIMESTAMP] Health check completed" >> $HEALTH_LOG
```

---

### RB-202: Análisis de Performance

#### Frecuencia
- **Tiempo real**: Dashboards de Grafana
- **Análisis profundo**: Semanal

#### Procedimiento Semanal (30 minutos)

**Paso 1: Recolección de Métricas (10 minutos)**
```bash
# Crear directorio para reporte
REPORT_DATE=$(date +%Y%m%d)
REPORT_DIR="/reports/performance_$REPORT_DATE"
mkdir -p $REPORT_DIR

# Exportar métricas de Prometheus
curl -G 'http://prometheus:9090/api/v1/query_range' \
  --data-urlencode 'query=rate(http_requests_total[5m])' \
  --data-urlencode 'start='$(date -d '7 days ago' --iso-8601) \
  --data-urlencode 'end='$(date --iso-8601) \
  --data-urlencode 'step=3600' \
  | jq . > $REPORT_DIR/http_requests_rate.json

# Métricas de ML Service
curl -G 'http://prometheus:9090/api/v1/query_range' \
  --data-urlencode 'query=ml_inference_time_seconds' \
  --data-urlencode 'start='$(date -d '7 days ago' --iso-8601) \
  --data-urlencode 'end='$(date --iso-8601) \
  --data-urlencode 'step=3600' \
  | jq . > $REPORT_DIR/ml_inference_time.json
```

**Paso 2: Análisis de Base de Datos (10 minutos)**
```bash
# Conectar a PostgreSQL y generar reporte
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
  psql -U trafficuser -d trafficdb -c "
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
  pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY size_bytes DESC;
" > $REPORT_DIR/database_sizes.txt

# Queries más lentas
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
  psql -U trafficuser -d trafficdb -c "
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 20;
" > $REPORT_DIR/slow_queries.txt
```

**Paso 3: Análisis de Logs (5 minutos)**
```bash
# Análisis de errores
kubectl logs -l app.kubernetes.io/name=traffic-system -n traffic-system --since=168h | \
  grep -i error | \
  sort | uniq -c | sort -nr > $REPORT_DIR/error_summary.txt

# Análisis de performance del ML
kubectl logs deployment/traffic-system-ml-service -n traffic-system --since=168h | \
  grep "inference_time" | \
  awk '{print $NF}' | \
  sort -n > $REPORT_DIR/ml_inference_times.txt
```

**Paso 4: Generación de Reporte (5 minutos)**
```bash
# Crear reporte consolidado
cat > $REPORT_DIR/performance_summary.md << EOF
# Performance Report - Week of $(date +%Y-%m-%d)

## Summary
- Report generated: $(date)
- Period: $(date -d '7 days ago' +%Y-%m-%d) to $(date +%Y-%m-%d)

## Key Metrics
- Average response time: $(curl -s 'http://prometheus:9090/api/v1/query?query=avg_over_time(http_request_duration_seconds[7d])' | jq -r '.data.result[0].value[1]') seconds
- Total requests: $(curl -s 'http://prometheus:9090/api/v1/query?query=increase(http_requests_total[7d])' | jq -r '.data.result[0].value[1]')
- Error rate: $(curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[7d])' | jq -r '.data.result[0].value[1]')%

## Database Performance
$(cat $REPORT_DIR/database_sizes.txt)

## Recommendations
$(if [ $(echo "$(curl -s 'http://prometheus:9090/api/v1/query?query=avg_over_time(http_request_duration_seconds[7d])' | jq -r '.data.result[0].value[1]') > 1.0" | bc) -eq 1 ]; then echo "- Consider optimizing slow queries"; fi)
$(if [ $(grep -c "OutOfMemory" $REPORT_DIR/error_summary.txt) -gt 0 ]; then echo "- Memory optimization needed"; fi)
EOF

# Enviar reporte por email
mail -s "Weekly Performance Report - $REPORT_DATE" \
  -a $REPORT_DIR/performance_summary.md \
  admin@trafficsystem.com < $REPORT_DIR/performance_summary.md
```

---

## 🔐 Procedimientos de Seguridad

### RB-301: Rotación de Credenciales

#### Frecuencia
- **Passwords de servicio**: Trimestral
- **API Keys**: Mensual
- **Certificados**: Según expiración

#### Procedimiento (25 minutos)

**Paso 1: Backup de Configuración Actual (2 minutos)**
```bash
# Backup de secrets actuales
kubectl get secrets -n traffic-system -o yaml > secrets_backup_$(date +%Y%m%d).yaml

# Backup de configuración
kubectl get configmap -n traffic-system -o yaml > configmap_backup_$(date +%Y%m%d).yaml
```

**Paso 2: Generar Nuevas Credenciales (5 minutos)**
```bash
# Generar nueva contraseña para PostgreSQL
NEW_PG_PASSWORD=$(openssl rand -base64 32)

# Generar nueva contraseña para Redis
NEW_REDIS_PASSWORD=$(openssl rand -base64 32)

# Generar nueva clave Django
NEW_DJANGO_SECRET=$(openssl rand -base64 50)

# Generar nuevas API keys
NEW_ML_API_KEY=$(openssl rand -hex 32)
NEW_CONFIG_API_KEY=$(openssl rand -hex 32)
```

**Paso 3: Actualizar PostgreSQL (8 minutos)**
```bash
# Conectar a PostgreSQL
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
  psql -U postgres -d postgres

# Cambiar contraseña del usuario de aplicación
ALTER USER trafficuser PASSWORD '$NEW_PG_PASSWORD';

# Verificar cambio
\du trafficuser

# Salir de PostgreSQL
\q

# Actualizar secret en Kubernetes
kubectl patch secret traffic-system-postgresql -n traffic-system -p="
{
  \"data\": {
    \"postgres-password\": \"$(echo -n $NEW_PG_PASSWORD | base64)\"
  }
}"
```

**Paso 4: Actualizar Redis (3 minutos)**
```bash
# Conectar a Redis
kubectl exec -it traffic-system-redis-master-0 -n traffic-system -- redis-cli

# Configurar nueva contraseña
CONFIG SET requirepass $NEW_REDIS_PASSWORD
CONFIG REWRITE

# Verificar nueva contraseña
AUTH $NEW_REDIS_PASSWORD
PING

# Salir de Redis
EXIT

# Actualizar secret en Kubernetes
kubectl patch secret traffic-system-redis -n traffic-system -p="
{
  \"data\": {
    \"redis-password\": \"$(echo -n $NEW_REDIS_PASSWORD | base64)\"
  }
}"
```

**Paso 5: Actualizar Secretos de Aplicación (5 minutos)**
```bash
# Actualizar Django secret key
kubectl patch secret traffic-system-secrets -n traffic-system -p="
{
  \"data\": {
    \"django-secret-key\": \"$(echo -n $NEW_DJANGO_SECRET | base64)\",
    \"ml-api-key\": \"$(echo -n $NEW_ML_API_KEY | base64)\",
    \"config-api-key\": \"$(echo -n $NEW_CONFIG_API_KEY | base64)\"
  }
}"

# Reiniciar servicios para aplicar nuevas credenciales
kubectl rollout restart deployment/traffic-system-backend -n traffic-system
kubectl rollout restart deployment/traffic-system-ml-service -n traffic-system
kubectl rollout restart deployment/traffic-system-config-service -n traffic-system

# Esperar que se reinicien
kubectl rollout status deployment/traffic-system-backend -n traffic-system
kubectl rollout status deployment/traffic-system-ml-service -n traffic-system
kubectl rollout status deployment/traffic-system-config-service -n traffic-system
```

**Paso 6: Verificación (2 minutos)**
```bash
# Probar conectividad de base de datos
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py check --database

# Probar Redis
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python -c "
import redis
import os
r = redis.Redis(
    host='traffic-system-redis-master',
    port=6379,
    password=os.environ.get('REDIS_PASSWORD')
)
print('Redis connection:', r.ping())
"

# Probar aplicación
curl -f https://traffic-system.domain.com/api/v1/health/
```

---

## 📝 Documentación y Comunicación

### Plantillas de Comunicación

#### Template: Incidente Crítico
```
ASUNTO: [CRÍTICO] Sistema de Tráfico - <Descripción breve>

Estimado equipo,

RESUMEN DEL INCIDENTE:
- Tiempo de inicio: <timestamp>
- Impacto: <descripción del impacto>
- Servicios afectados: <lista de servicios>
- Estado actual: <En investigación/Resolviendo/Resuelto>

ACCIONES TOMADAS:
- <acción 1>
- <acción 2>

PRÓXIMOS PASOS:
- <paso 1>
- <paso 2>

ETA DE RESOLUCIÓN: <estimación>

Actualizaré en <frecuencia> o cuando haya cambios significativos.

<nombre>
<contacto>
```

#### Template: Mantenimiento Programado
```
ASUNTO: [MANTENIMIENTO] Sistema de Tráfico - <fecha y hora>

Estimados usuarios,

Se ha programado un mantenimiento para el Sistema de Detección de Infracciones:

DETALLES:
- Fecha: <fecha>
- Hora inicio: <hora inicio>
- Duración estimada: <duración>
- Hora fin estimada: <hora fin>

SERVICIOS AFECTADOS:
- <servicio 1>: <tipo de impacto>
- <servicio 2>: <tipo de impacto>

RAZÓN DEL MANTENIMIENTO:
<descripción del motivo>

PREPARACIÓN REQUERIDA:
- <acción 1>
- <acción 2>

Para preguntas, contactar: support@trafficsystem.com

Gracias por su comprensión.
```

### Checklist de Post-Incidente

#### Análisis Post-Mortem
- [ ] **Timeline detallado** del incidente documentado
- [ ] **Root cause analysis** completado
- [ ] **Impact assessment** cuantificado
- [ ] **Lessons learned** identificadas
- [ ] **Action items** definidos con owners y fechas
- [ ] **Documentation** actualizada
- [ ] **Runbooks** mejorados según aprendizajes
- [ ] **Monitoring** mejorado para prevenir recurrencia
- [ ] **Training** adicional programado si es necesario
- [ ] **Stakeholders** informados de resultados y acciones

---

**Contactos de Escalamiento:**
- **L1 Support**: support@trafficsystem.com
- **L2 Engineering**: engineering@trafficsystem.com  
- **L3 Architecture**: architecture@trafficsystem.com
- **Emergency**: +1-800-TRAFFIC

**Herramientas Requeridas:**
- kubectl configurado
- Acceso a Grafana/Prometheus
- Credenciales de AWS/Azure/GCP
- Acceso a repositorios Git
- Herramientas de backup configuradas