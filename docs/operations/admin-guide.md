# Guía de Administración del Sistema

## Introducción

Esta guía proporciona las instrucciones necesarias para administrar el Sistema de Detección de Infracciones de Tráfico en un entorno de producción. Incluye tareas rutinarias, procedimientos de mantenimiento, y mejores prácticas operacionales.

## 1. Tareas de Administración Diarias

### Verificación de Estado del Sistema

#### Script de Verificación Matutina
```bash
#!/bin/bash
# daily-check.sh - Verificación diaria del sistema

echo "=== Daily System Health Check - $(date) ==="

# 1. Verificar estado de pods
echo "1. Pod Status:"
kubectl get pods -n traffic-system --field-selector=status.phase!=Running

# 2. Verificar uso de recursos
echo "2. Resource Usage:"
kubectl top nodes
kubectl top pods -n traffic-system --sort-by=cpu

# 3. Verificar almacenamiento
echo "3. Storage Usage:"
kubectl get pvc -n traffic-system
df -h | grep -E "(disk|vol)"

# 4. Verificar servicios críticos
echo "4. Service Health:"
for service in backend ml-service config-service postgresql redis; do
  echo "Checking $service..."
  kubectl get pods -l app.kubernetes.io/component=$service -n traffic-system
done

# 5. Verificar métricas de negocio
echo "5. Business Metrics:"
curl -s http://prometheus:9090/api/v1/query?query=infractions_detected_total | jq '.data.result[0].value[1]'

# 6. Verificar alertas activas
echo "6. Active Alerts:"
curl -s http://alertmanager:9093/api/v1/alerts | jq '.data[] | select(.status.state=="firing") | .labels.alertname'

echo "=== Check Complete ==="
```

#### Dashboard de Monitoreo
Acceder diariamente a:
- **Grafana Dashboard**: `https://grafana.trafficsystem.com`
- **Prometheus Alerts**: `https://prometheus.trafficsystem.com/alerts`
- **Application Logs**: `https://kibana.trafficsystem.com`

### Revisión de Logs

#### Logs Críticos a Revisar
```bash
# Errores en el backend
kubectl logs -l app.kubernetes.io/component=backend -n traffic-system --since=24h | grep -i error

# Errores en ML Service
kubectl logs -l app.kubernetes.io/component=ml-service -n traffic-system --since=24h | grep -i "error\|exception"

# Eventos de Kubernetes
kubectl get events -n traffic-system --sort-by='.lastTimestamp' | tail -50

# Logs de base de datos
kubectl logs traffic-system-postgresql-0 -n traffic-system --since=24h | grep -i "error\|fatal"
```

### Limpieza de Archivos Temporales
```bash
# Limpiar archivos temporales del ML Service
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
  find /tmp -name "*.jpg" -o -name "*.mp4" -mtime +1 -delete

# Limpiar logs antiguos
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  find /app/logs -name "*.log" -mtime +7 -delete

# Limpiar cache de Redis si es necesario
kubectl exec -it traffic-system-redis-master-0 -n traffic-system -- \
  redis-cli FLUSHDB
```

## 2. Tareas Semanales

### Backup Completo del Sistema

#### Backup de Base de Datos
```bash
#!/bin/bash
# weekly-backup.sh

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/weekly"

# Crear directorio de backup
mkdir -p $BACKUP_DIR

# Backup de PostgreSQL
kubectl exec traffic-system-postgresql-0 -n traffic-system -- \
  pg_dump -U trafficuser -d trafficdb | \
  gzip > $BACKUP_DIR/postgresql_$BACKUP_DATE.sql.gz

# Backup de Redis
kubectl exec traffic-system-redis-master-0 -n traffic-system -- \
  redis-cli BGSAVE

kubectl cp traffic-system-redis-master-0:/data/dump.rdb \
  $BACKUP_DIR/redis_$BACKUP_DATE.rdb -n traffic-system

# Backup de MinIO
kubectl exec deployment/traffic-system-minio -n traffic-system -- \
  mc mirror --overwrite myminio/evidence $BACKUP_DIR/minio_$BACKUP_DATE/

# Backup de configuraciones de Kubernetes
kubectl get all,configmap,secret,pvc -n traffic-system -o yaml > \
  $BACKUP_DIR/kubernetes_config_$BACKUP_DATE.yaml

echo "Backup completed: $BACKUP_DATE"
```

#### Sincronización con Cloud Storage
```bash
# Sincronizar backups con AWS S3
aws s3 sync /backups/weekly s3://traffic-system-backups/weekly/

# Limpiar backups locales antiguos (mantener 4 semanas)
find /backups/weekly -name "*.gz" -mtime +28 -delete
```

### Análisis de Performance

#### Reporte de Performance Semanal
```bash
#!/bin/bash
# weekly-performance-report.sh

REPORT_DATE=$(date +%Y%m%d)

echo "=== Weekly Performance Report - $REPORT_DATE ===" > weekly_report_$REPORT_DATE.txt

# Métricas de CPU y Memoria
echo "1. Resource Utilization:" >> weekly_report_$REPORT_DATE.txt
kubectl top nodes >> weekly_report_$REPORT_DATE.txt
kubectl top pods -n traffic-system --sort-by=cpu >> weekly_report_$REPORT_DATE.txt

# Estadísticas de infracciones
echo "2. Infraction Statistics:" >> weekly_report_$REPORT_DATE.txt
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from infractions.models import Infraction
from datetime import datetime, timedelta
import django.utils.timezone as tz

last_week = tz.now() - timedelta(days=7)
total = Infraction.objects.filter(created_at__gte=last_week).count()
confirmed = Infraction.objects.filter(created_at__gte=last_week, status='confirmed').count()
accuracy = (confirmed / total * 100) if total > 0 else 0

print(f'Total infractions: {total}')
print(f'Confirmed infractions: {confirmed}')
print(f'Accuracy: {accuracy:.2f}%')
" >> weekly_report_$REPORT_DATE.txt

# Métricas de ML Service
echo "3. ML Service Metrics:" >> weekly_report_$REPORT_DATE.txt
curl -s http://prometheus:9090/api/v1/query?query=avg_over_time\(ml_inference_time_seconds\[7d\]\) | \
  jq -r '.data.result[0].value[1]' >> weekly_report_$REPORT_DATE.txt

# Enviar reporte por email
mail -s "Weekly Performance Report - $REPORT_DATE" admin@trafficsystem.com < weekly_report_$REPORT_DATE.txt
```

### Actualización de Certificados SSL
```bash
# Verificar expiración de certificados
kubectl get certificate -n traffic-system

# Renovar certificados Let's Encrypt automáticamente
kubectl annotate certificate traffic-system-tls -n traffic-system \
  cert-manager.io/issue-temporary-certificate="true"

# Verificar nuevo certificado
kubectl describe certificate traffic-system-tls -n traffic-system
```

## 3. Tareas Mensuales

### Revisión de Capacidad

#### Análisis de Crecimiento
```bash
#!/bin/bash
# monthly-capacity-review.sh

echo "=== Monthly Capacity Review - $(date +%Y-%m) ==="

# Análisis de crecimiento de datos
echo "1. Database Growth:"
kubectl exec traffic-system-postgresql-0 -n traffic-system -- \
  psql -U trafficuser -d trafficdb -c "
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Análisis de uso de almacenamiento
echo "2. Storage Usage:"
kubectl exec deployment/traffic-system-minio -n traffic-system -- \
  mc du --depth=1 myminio/

# Proyección de crecimiento
echo "3. Growth Projection:"
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from infractions.models import Infraction
from datetime import datetime, timedelta
import django.utils.timezone as tz

# Cálculo de crecimiento mensual
current_month = tz.now().replace(day=1)
last_month = (current_month - timedelta(days=1)).replace(day=1)

current_count = Infraction.objects.filter(created_at__gte=current_month).count()
last_count = Infraction.objects.filter(
    created_at__gte=last_month,
    created_at__lt=current_month
).count()

growth_rate = ((current_count - last_count) / last_count * 100) if last_count > 0 else 0
projected_next_month = current_count * (1 + growth_rate/100)

print(f'Current month infractions: {current_count}')
print(f'Last month infractions: {last_count}')
print(f'Growth rate: {growth_rate:.2f}%')
print(f'Projected next month: {int(projected_next_month)}')
"
```

#### Recomendaciones de Escalamiento
```bash
# Verificar HPA status
kubectl get hpa -n traffic-system

# Analizar patrones de uso
kubectl top pods -n traffic-system --sort-by=cpu

# Recomendaciones automáticas
if [[ $(kubectl get hpa traffic-system-backend -n traffic-system -o jsonpath='{.status.currentReplicas}') -gt 5 ]]; then
  echo "RECOMMENDATION: Consider increasing backend resources"
fi

if [[ $(kubectl get hpa traffic-system-ml-service -n traffic-system -o jsonpath='{.status.currentReplicas}') -gt 3 ]]; then
  echo "RECOMMENDATION: Consider adding ML nodes with GPU"
fi
```

### Actualización de Sistema

#### Proceso de Actualización Mensual
```bash
#!/bin/bash
# monthly-update.sh

echo "=== Monthly System Update - $(date +%Y-%m) ==="

# 1. Backup completo antes de actualización
./weekly-backup.sh

# 2. Actualizar imágenes Docker
docker pull trafficsystem/backend:latest
docker pull trafficsystem/ml-service:latest
docker pull trafficsystem/config-service:latest
docker pull trafficsystem/frontend:latest

# 3. Actualizar Helm charts
helm repo update

# 4. Actualizar sistema (rolling update)
helm upgrade traffic-system ./helm \
  --namespace traffic-system \
  --set images.backend.tag=latest \
  --set images.mlService.tag=latest \
  --set images.configService.tag=latest \
  --set images.frontend.tag=latest

# 5. Verificar actualización
kubectl rollout status deployment/traffic-system-backend -n traffic-system
kubectl rollout status deployment/traffic-system-ml-service -n traffic-system

# 6. Ejecutar tests de smoke
./smoke-tests.sh

echo "Update completed successfully"
```

### Revisión de Seguridad

#### Auditoría de Seguridad Mensual
```bash
#!/bin/bash
# monthly-security-audit.sh

echo "=== Monthly Security Audit - $(date +%Y-%m) ==="

# 1. Verificar vulnerabilidades en imágenes
echo "1. Container Image Vulnerabilities:"
trivy image trafficsystem/backend:latest
trivy image trafficsystem/ml-service:latest

# 2. Verificar configuraciones de seguridad
echo "2. Security Configurations:"
kubectl get pod -n traffic-system -o jsonpath='{.items[*].spec.securityContext}'

# 3. Verificar Network Policies
echo "3. Network Policies:"
kubectl get networkpolicy -n traffic-system

# 4. Verificar RBAC
echo "4. RBAC Configuration:"
kubectl get rolebinding,clusterrolebinding -n traffic-system

# 5. Auditar accesos
echo "5. Access Audit:"
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.contrib.auth.models import User
from datetime import datetime, timedelta

last_month = datetime.now() - timedelta(days=30)
active_users = User.objects.filter(last_login__gte=last_month)
inactive_users = User.objects.filter(last_login__lt=last_month)

print(f'Active users (last 30 days): {active_users.count()}')
print(f'Inactive users: {inactive_users.count()}')

for user in inactive_users:
    print(f'Inactive: {user.username} - Last login: {user.last_login}')
"

# 6. Verificar certificados
echo "6. Certificate Status:"
kubectl get certificate -n traffic-system -o custom-columns=NAME:.metadata.name,READY:.status.conditions[0].status,AGE:.metadata.creationTimestamp
```

## 4. Gestión de Usuarios

### Crear Nuevo Usuario
```bash
#!/bin/bash
# create-user.sh

read -p "Username: " USERNAME
read -p "Email: " EMAIL
read -p "First Name: " FIRSTNAME
read -p "Last Name: " LASTNAME
read -p "Role (admin/operator/viewer): " ROLE

kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.contrib.auth.models import User, Group
from authentication.models import UserProfile

# Crear usuario
user = User.objects.create_user(
    username='$USERNAME',
    email='$EMAIL',
    first_name='$FIRSTNAME',
    last_name='$LASTNAME',
    password='temp_password_123'
)

# Asignar rol
group = Group.objects.get(name='${ROLE}s')
user.groups.add(group)

# Crear perfil
profile = UserProfile.objects.create(
    user=user,
    role='$ROLE'
)

print(f'User {user.username} created successfully')
print(f'Temporary password: temp_password_123')
print(f'User must change password on first login')
"
```

### Gestión de Permisos
```bash
# Listar usuarios y sus roles
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.contrib.auth.models import User

for user in User.objects.all():
    groups = ', '.join([g.name for g in user.groups.all()])
    print(f'{user.username}: {groups} (Active: {user.is_active})')
"

# Cambiar rol de usuario
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.contrib.auth.models import User, Group

user = User.objects.get(username='usuario_ejemplo')
user.groups.clear()
new_group = Group.objects.get(name='operators')
user.groups.add(new_group)
print(f'User {user.username} role updated to operator')
"

# Desactivar usuario
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.contrib.auth.models import User

user = User.objects.get(username='usuario_ejemplo')
user.is_active = False
user.save()
print(f'User {user.username} deactivated')
"
```

## 5. Gestión de Configuración

### Backup de Configuración
```bash
# Exportar toda la configuración
kubectl get configmap,secret -n traffic-system -o yaml > config-backup-$(date +%Y%m%d).yaml

# Backup específico del Config Service
kubectl exec -it deployment/traffic-system-config-service -n traffic-system -- \
  tar -czf /tmp/config-backup-$(date +%Y%m%d).tar.gz /app/config/

kubectl cp traffic-system-config-service:/tmp/config-backup-$(date +%Y%m%d).tar.gz \
  ./config-backup-$(date +%Y%m%d).tar.gz -n traffic-system
```

### Actualizar Configuración
```bash
# Actualizar configuración a través del Config Service
curl -X PUT http://config-service:8002/config \
  -H "Content-Type: application/json" \
  -d '{
    "detection": {
      "confidence_threshold": 0.85
    },
    "notifications": {
      "email_enabled": true
    }
  }'

# Verificar cambios
curl http://config-service:8002/config | jq .
```

### Rollback de Configuración
```bash
# Listar versiones de configuración
curl http://config-service:8002/config/versions

# Hacer rollback a versión anterior
curl -X POST http://config-service:8002/config/rollback \
  -H "Content-Type: application/json" \
  -d '{"version": "v1.2.3"}'
```

## 6. Monitoreo y Alertas

### Configuración de Alertas Críticas
```yaml
# critical-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: traffic-system-critical-alerts
spec:
  groups:
  - name: critical
    rules:
    - alert: ServiceDown
      expr: up{job="traffic-system"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Service {{ $labels.job }} is down"
    
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
    
    - alert: DatabaseConnectionFailed
      expr: pg_up == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Database connection failed"
```

### Dashboard Personalizado
```json
{
  "dashboard": {
    "title": "Traffic System Admin Dashboard",
    "panels": [
      {
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"traffic-system\"}",
            "legendFormat": "{{ instance }}"
          }
        ]
      },
      {
        "title": "Infraction Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(infractions_detected_total[5m])",
            "legendFormat": "Infractions/sec"
          }
        ]
      }
    ]
  }
}
```

## 7. Procedimientos de Emergencia

### Escalamiento de Emergencia
```bash
#!/bin/bash
# emergency-scale.sh

echo "Applying emergency scaling..."

# Escalar servicios críticos
kubectl scale deployment traffic-system-backend --replicas=10 -n traffic-system
kubectl scale deployment traffic-system-ml-service --replicas=5 -n traffic-system

# Aumentar recursos de base de datos
helm upgrade traffic-system ./helm \
  --set postgresql.primary.resources.limits.cpu=4000m \
  --set postgresql.primary.resources.limits.memory=8Gi

echo "Emergency scaling applied"
```

### Modo de Solo Lectura
```bash
# Activar modo de solo lectura
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.conf import settings
from django.core.cache import cache

cache.set('SYSTEM_READ_ONLY', True, timeout=None)
print('System set to read-only mode')
"

# Desactivar modo de solo lectura
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.core.cache import cache

cache.delete('SYSTEM_READ_ONLY')
print('Read-only mode disabled')
"
```

## 8. Reportes Administrativos

### Reporte de Uso de Recursos
```bash
#!/bin/bash
# resource-usage-report.sh

echo "=== Resource Usage Report - $(date) ===" > resource_report.txt

echo "1. Node Resources:" >> resource_report.txt
kubectl top nodes >> resource_report.txt

echo "2. Pod Resources:" >> resource_report.txt
kubectl top pods -n traffic-system --sort-by=cpu >> resource_report.txt

echo "3. Storage Usage:" >> resource_report.txt
kubectl get pvc -n traffic-system >> resource_report.txt

echo "4. Network Usage:" >> resource_report.txt
kubectl get svc -n traffic-system >> resource_report.txt

# Enviar por email
mail -s "Resource Usage Report - $(date +%Y-%m-%d)" admin@trafficsystem.com < resource_report.txt
```

### Reporte de Actividad de Usuarios
```bash
# user-activity-report.sh
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from datetime import datetime, timedelta

print('=== User Activity Report ===')
print(f'Report Date: {datetime.now().strftime(\"%Y-%m-%d\")}')

# Usuarios activos en los últimos 7 días
last_week = datetime.now() - timedelta(days=7)
active_users = User.objects.filter(last_login__gte=last_week)

print(f'\\nActive Users (last 7 days): {active_users.count()}')
for user in active_users:
    print(f'- {user.username}: {user.last_login}')

# Actividad de logs
recent_actions = LogEntry.objects.filter(action_time__gte=last_week)
print(f'\\nTotal actions: {recent_actions.count()}')

# Top usuarios por actividad
from django.db.models import Count
top_users = recent_actions.values('user__username').annotate(
    action_count=Count('id')
).order_by('-action_count')[:10]

print('\\nTop 10 Most Active Users:')
for user_data in top_users:
    print(f'- {user_data[\"user__username\"]}: {user_data[\"action_count\"]} actions')
"
```

Esta guía proporciona los procedimientos necesarios para mantener el sistema funcionando de manera óptima. Todos los scripts deben ser ejecutados por personal autorizado y siguiendo los protocolos de cambio establecidos.