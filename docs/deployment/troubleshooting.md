# Guía de Troubleshooting - Sistema de Detección de Infracciones

## Problemas Comunes y Soluciones

### 1. Problemas de Conectividad

#### Frontend no puede conectar al Backend
**Síntomas:**
- Error 502 Bad Gateway
- Timeouts en requests
- "Network Error" en la interfaz

**Diagnóstico:**
```bash
# Verificar estado de servicios
kubectl get pods -n traffic-system
kubectl get svc -n traffic-system

# Verificar logs del ingress
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Probar conectividad directa
kubectl port-forward svc/traffic-system-backend 8000:8000 -n traffic-system
curl http://localhost:8000/api/v1/health/
```

**Soluciones:**
1. **Verificar configuración de Ingress:**
   ```bash
   kubectl describe ingress traffic-system -n traffic-system
   ```

2. **Revisar DNS y configuración:**
   ```bash
   # Verificar resolución DNS
   nslookup traffic-system.yourdomain.com
   
   # Verificar certificados TLS
   kubectl get certificate -n traffic-system
   ```

3. **Reiniciar servicios:**
   ```bash
   kubectl rollout restart deployment/traffic-system-backend -n traffic-system
   ```

#### Base de Datos Inaccesible
**Síntomas:**
- Error "Unable to connect to database"
- Timeouts en queries
- 500 Internal Server Error

**Diagnóstico:**
```bash
# Verificar estado de PostgreSQL
kubectl get pods -l app.kubernetes.io/name=postgresql -n traffic-system
kubectl logs traffic-system-postgresql-0 -n traffic-system

# Probar conexión directa
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- psql -U trafficuser -d trafficdb
```

**Soluciones:**
1. **Verificar recursos:**
   ```bash
   kubectl describe pod traffic-system-postgresql-0 -n traffic-system
   kubectl top pod traffic-system-postgresql-0 -n traffic-system
   ```

2. **Revisar configuración de conexión:**
   ```bash
   kubectl get secret traffic-system-postgresql -n traffic-system -o yaml
   ```

3. **Restaurar desde backup:**
   ```bash
   # Ver procedimiento completo en backup.md
   kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
     pg_restore -U trafficuser -d trafficdb /backup/latest.dump
   ```

### 2. Problemas de Performance

#### Alto Tiempo de Respuesta en ML Service
**Síntomas:**
- Timeouts en detección de placas
- Cola de requests acumulándose
- CPU/GPU al 100%

**Diagnóstico:**
```bash
# Verificar recursos del ML Service
kubectl top pod -l app.kubernetes.io/component=ml-service -n traffic-system

# Verificar métricas de GPU
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- nvidia-smi

# Revisar logs para errores
kubectl logs -f deployment/traffic-system-ml-service -n traffic-system
```

**Soluciones:**
1. **Escalar horizontalmente:**
   ```bash
   kubectl scale deployment traffic-system-ml-service --replicas=5 -n traffic-system
   ```

2. **Optimizar configuración:**
   ```bash
   # Actualizar límites de recursos
   kubectl patch deployment traffic-system-ml-service -n traffic-system -p='
   {
     "spec": {
       "template": {
         "spec": {
           "containers": [{
             "name": "ml-service",
             "resources": {
               "limits": {"cpu": "4000m", "memory": "8Gi"},
               "requests": {"cpu": "2000m", "memory": "4Gi"}
             }
           }]
         }
       }
     }
   }'
   ```

3. **Limpiar cache de modelos:**
   ```bash
   kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
     rm -rf /app/model_cache/*
   ```

#### Base de Datos Lenta
**Síntomas:**
- Queries lentos
- Timeouts en el backend
- Alto CPU en PostgreSQL

**Diagnóstico:**
```bash
# Conectar a la base de datos
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
  psql -U trafficuser -d trafficdb

# Verificar queries lentos
SELECT query, mean_time, calls FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

# Verificar índices faltantes
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats WHERE schemaname = 'public';
```

**Soluciones:**
1. **Optimizar queries:**
   ```sql
   -- Analizar plan de ejecución
   EXPLAIN ANALYZE SELECT * FROM infractions WHERE created_at > NOW() - INTERVAL '1 day';
   
   -- Crear índices necesarios
   CREATE INDEX idx_infractions_created_at ON infractions(created_at);
   CREATE INDEX idx_infractions_status ON infractions(status);
   ```

2. **Configurar PostgreSQL:**
   ```bash
   # Editar configuración
   kubectl edit configmap traffic-system-postgresql-config -n traffic-system
   
   # Agregar configuraciones de performance
   shared_buffers = 256MB
   effective_cache_size = 1GB
   work_mem = 4MB
   ```

3. **Escalar base de datos:**
   ```bash
   # Aumentar recursos
   helm upgrade traffic-system ./helm \
     --set postgresql.primary.resources.limits.cpu=2000m \
     --set postgresql.primary.resources.limits.memory=4Gi
   ```

### 3. Problemas de Almacenamiento

#### Disco Lleno
**Síntomas:**
- Error "No space left on device"
- Pods en estado CrashLoopBackOff
- Logs indicando problemas de escritura

**Diagnóstico:**
```bash
# Verificar uso de almacenamiento
kubectl get pvc -n traffic-system
kubectl describe pvc -n traffic-system

# Verificar espacio en nodos
kubectl get nodes -o wide
kubectl describe node <node-name>
```

**Soluciones:**
1. **Limpiar archivos temporales:**
   ```bash
   # Limpiar logs antiguos
   kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
     find /app/logs -name "*.log" -mtime +7 -delete
   
   # Limpiar cache de imágenes
   kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
     find /tmp -name "*.jpg" -mtime +1 -delete
   ```

2. **Expandir volúmenes:**
   ```bash
   # Expandir PVC (si el storage class lo permite)
   kubectl patch pvc traffic-system-shared-storage -n traffic-system -p='
   {
     "spec": {
       "resources": {
         "requests": {
           "storage": "200Gi"
         }
       }
     }
   }'
   ```

3. **Configurar rotación de logs:**
   ```yaml
   # Agregar a deployment
   volumeMounts:
   - name: logs
     mountPath: /app/logs
   volumes:
   - name: logs
     emptyDir:
       sizeLimit: 10Gi
   ```

#### MinIO Storage Issues
**Síntomas:**
- Error al subir archivos
- Objetos corruptos
- Slow upload/download

**Diagnóstico:**
```bash
# Verificar estado de MinIO
kubectl get pods -l app.kubernetes.io/name=minio -n traffic-system
kubectl logs deployment/traffic-system-minio -n traffic-system

# Probar conectividad
kubectl port-forward svc/traffic-system-minio 9000:9000 -n traffic-system
# Acceder a http://localhost:9000
```

**Soluciones:**
1. **Verificar configuración:**
   ```bash
   kubectl get secret traffic-system-minio -n traffic-system -o yaml
   ```

2. **Limpiar objetos corruptos:**
   ```bash
   kubectl exec -it deployment/traffic-system-minio -n traffic-system -- \
     mc admin heal myminio --recursive
   ```

3. **Rebalancear datos:**
   ```bash
   kubectl exec -it deployment/traffic-system-minio -n traffic-system -- \
     mc admin rebalance myminio
   ```

### 4. Problemas de Autenticación

#### JWT Token Errors
**Síntomas:**
- Error "Invalid token"
- Usuarios no pueden loguearse
- Tokens expiran inmediatamente

**Diagnóstico:**
```bash
# Verificar configuración de JWT
kubectl get secret traffic-system-secrets -n traffic-system -o yaml

# Verificar logs del backend
kubectl logs deployment/traffic-system-backend -n traffic-system | grep -i jwt
```

**Soluciones:**
1. **Regenerar secret key:**
   ```bash
   # Generar nueva clave
   NEW_SECRET=$(openssl rand -base64 32)
   
   # Actualizar secret
   kubectl patch secret traffic-system-secrets -n traffic-system -p="
   {
     \"data\": {
       \"django-secret-key\": \"$(echo -n $NEW_SECRET | base64)\"
     }
   }"
   
   # Reiniciar backend
   kubectl rollout restart deployment/traffic-system-backend -n traffic-system
   ```

2. **Verificar timezone:**
   ```bash
   # Verificar timezone en containers
   kubectl exec -it deployment/traffic-system-backend -n traffic-system -- date
   
   # Sincronizar con NTP si es necesario
   kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
     ntpdate -s time.google.com
   ```

#### Permission Denied
**Síntomas:**
- Error 403 Forbidden
- Usuarios no pueden acceder a recursos
- RBAC errors

**Diagnóstico:**
```bash
# Verificar permisos de usuario
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='problematic_user')
print(user.groups.all())
print(user.user_permissions.all())
"
```

**Soluciones:**
1. **Corregir permisos:**
   ```bash
   kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
     python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.get(username='problematic_user')
group = Group.objects.get(name='operators')
user.groups.add(group)
"
   ```

2. **Resetear permisos:**
   ```bash
   kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
     python manage.py migrate --run-syncdb
   ```

### 5. Problemas de Red

#### DNS Resolution Issues
**Síntomas:**
- "Service not found" errors
- Intermittent connectivity
- Cross-service communication fails

**Diagnóstico:**
```bash
# Verificar DNS en cluster
kubectl run test-pod --image=busybox -it --rm -- nslookup kubernetes.default

# Verificar servicios
kubectl get svc -n traffic-system
kubectl describe svc traffic-system-backend -n traffic-system
```

**Soluciones:**
1. **Verificar CoreDNS:**
   ```bash
   kubectl get pods -n kube-system -l k8s-app=kube-dns
   kubectl logs -n kube-system deployment/coredns
   ```

2. **Reiniciar DNS:**
   ```bash
   kubectl rollout restart deployment/coredns -n kube-system
   ```

#### Network Policy Issues
**Síntomas:**
- Connections blocked between services
- Timeouts en comunicación interna

**Diagnóstico:**
```bash
# Verificar network policies
kubectl get networkpolicy -n traffic-system
kubectl describe networkpolicy -n traffic-system

# Probar conectividad
kubectl run test-pod --image=busybox -it --rm -- \
  wget -qO- traffic-system-backend:8000/health/
```

**Soluciones:**
1. **Ajustar network policies:**
   ```bash
   # Permitir tráfico temporalmente
   kubectl patch networkpolicy default-deny -n traffic-system -p='
   {
     "spec": {
       "policyTypes": []
     }
   }'
   ```

2. **Crear policy específica:**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: allow-frontend-to-backend
   spec:
     podSelector:
       matchLabels:
         app.kubernetes.io/component: backend
     policyTypes:
     - Ingress
     ingress:
     - from:
       - podSelector:
           matchLabels:
             app.kubernetes.io/component: frontend
   ```

### 6. Problemas de Monitoreo

#### Prometheus No Collecta Métricas
**Síntomas:**
- Dashboards vacíos en Grafana
- Métricas faltantes
- Alertas no funcionan

**Diagnóstico:**
```bash
# Verificar Prometheus
kubectl get pods -l app.kubernetes.io/name=prometheus -n traffic-system
kubectl logs deployment/traffic-system-prometheus-server -n traffic-system

# Verificar targets
kubectl port-forward svc/traffic-system-prometheus-server 9090:80 -n traffic-system
# Acceder a http://localhost:9090/targets
```

**Soluciones:**
1. **Verificar service monitors:**
   ```bash
   kubectl get servicemonitor -n traffic-system
   kubectl describe servicemonitor traffic-system -n traffic-system
   ```

2. **Corregir configuración:**
   ```bash
   # Verificar configuración de Prometheus
   kubectl get configmap traffic-system-prometheus-server -n traffic-system -o yaml
   ```

3. **Reiniciar Prometheus:**
   ```bash
   kubectl rollout restart deployment/traffic-system-prometheus-server -n traffic-system
   ```

## Procedimientos de Emergencia

### 1. Rollback Completo
```bash
# Rollback usando Helm
helm rollback traffic-system 1 -n traffic-system

# Verificar estado
helm status traffic-system -n traffic-system
kubectl get pods -n traffic-system
```

### 2. Backup de Emergencia
```bash
# Backup de base de datos
kubectl exec traffic-system-postgresql-0 -n traffic-system -- \
  pg_dump -U trafficuser trafficdb > emergency-backup-$(date +%Y%m%d).sql

# Backup de configuración
kubectl get all -n traffic-system -o yaml > emergency-config-$(date +%Y%m%d).yaml
```

### 3. Modo de Mantenimiento
```bash
# Activar modo de mantenimiento
kubectl scale deployment traffic-system-frontend --replicas=0 -n traffic-system

# Mostrar página de mantenimiento
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: maintenance-page
data:
  index.html: |
    <html><body><h1>Sistema en Mantenimiento</h1></body></html>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maintenance-page
spec:
  replicas: 1
  selector:
    matchLabels:
      app: maintenance
  template:
    metadata:
      labels:
        app: maintenance
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html
      volumes:
      - name: html
        configMap:
          name: maintenance-page
EOF
```

## Herramientas de Diagnóstico

### 1. Scripts de Diagnóstico Automático
```bash
#!/bin/bash
# health-check.sh
echo "=== Traffic System Health Check ==="

echo "1. Checking pods..."
kubectl get pods -n traffic-system

echo "2. Checking services..."
kubectl get svc -n traffic-system

echo "3. Checking storage..."
kubectl get pvc -n traffic-system

echo "4. Checking resources..."
kubectl top pods -n traffic-system

echo "5. Checking recent events..."
kubectl get events -n traffic-system --sort-by='.lastTimestamp' | tail -20
```

### 2. Log Aggregation
```bash
# Recopilar todos los logs
kubectl logs -l app.kubernetes.io/name=traffic-system -n traffic-system \
  --tail=1000 > system-logs-$(date +%Y%m%d).log
```

### 3. Performance Profiling
```bash
# CPU profiling
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python -m cProfile -o profile.stats manage.py check

# Memory profiling
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
  python -m memory_profiler main.py
```

## Contactos de Soporte

### Escalation Matrix
1. **L1 Support**: Problemas básicos y reinicios
2. **L2 Support**: Problemas de configuración y performance
3. **L3 Support**: Problemas de arquitectura y desarrollo
4. **Emergency**: Problemas críticos de producción

### Canales de Comunicación
- **Slack**: #traffic-system-support
- **Email**: support@trafficsystem.com
- **Phone**: +1-800-TRAFFIC (24/7)
- **Incident Management**: PagerDuty integration

### Información para Reportes
Incluir siempre:
1. Descripción del problema
2. Pasos para reproducir
3. Logs relevantes
4. Configuración del entorno
5. Impacto en usuarios
6. Timeline del incidente