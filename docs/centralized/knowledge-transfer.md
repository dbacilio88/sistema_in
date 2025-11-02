# Procedimientos de Transferencia de Conocimiento - Sistema de Detección de Infracciones

## Introducción

La transferencia de conocimiento es el proceso final y crítico que asegura la continuidad operacional del Sistema de Detección de Infracciones de Tráfico. Este documento establece los procedimientos, herramientas y metodologías para una transferencia exitosa del conocimiento técnico y operacional.

## 🎯 Objetivos de la Transferencia

### Objetivos Primarios
- **Autonomía Operacional**: El equipo interno debe poder operar el sistema independientemente
- **Continuidad del Servicio**: Cero interrupciones durante la transición
- **Capacidad de Mantenimiento**: Habilidad para realizar mantenimientos preventivos y correctivos
- **Escalabilidad Futura**: Comprensión para implementar mejoras y expansiones

### Objetivos Secundarios
- **Optimización de Costos**: Reducir dependencia de consultores externos
- **Desarrollo de Capacidades**: Fortalecer competencias técnicas internas
- **Documentación Viva**: Establecer procesos de actualización documental
- **Cultura de Mejora Continua**: Implementar procesos de evolución del sistema

## 📋 Fases de Transferencia

### Fase 1: Preparación (Semanas 1-2)

#### 1.1 Evaluación de Competencias Actuales

**Actividades:**
- Assessment técnico individual por rol
- Identificación de brechas de conocimiento
- Plan personalizado de capacitación
- Asignación de mentores técnicos

**Entregables:**
- Matriz de competencias por persona
- Plan de capacitación individual
- Cronograma de actividades

**Criterios de Éxito:**
- ✅ 100% del personal evaluado
- ✅ Planes individuales aprobados
- ✅ Recursos de capacitación identificados

#### 1.2 Configuración del Entorno de Aprendizaje

**Actividades:**
```bash
# Crear entorno de sandbox para práctica
kubectl create namespace training-environment

# Desplegar versión de entrenamiento
helm install training-system ./helm \
  --namespace training-environment \
  --values values-training.yaml

# Configurar accesos de solo lectura a producción
kubectl create clusterrole training-viewer \
  --verb=get,list,watch \
  --resource=pods,services,deployments,configmaps

# Crear cuentas de entrenamiento
for user in trainee1 trainee2 trainee3; do
  kubectl create serviceaccount $user -n training-environment
  kubectl create clusterrolebinding ${user}-binding \
    --clusterrole=training-viewer \
    --serviceaccount=training-environment:$user
done
```

### Fase 2: Transferencia Técnica (Semanas 3-6)

#### 2.1 Arquitectura del Sistema

**Sesión 1: Vista General (4 horas)**

**Agenda:**
1. **Introducción a la Arquitectura (60 min)**
   - Diagrama de componentes
   - Flujo de datos principal
   - Patrones de diseño utilizados
   - Decisiones arquitectónicas

2. **Microservicios y APIs (90 min)**
   - Backend Django: Funcionalidades y endpoints
   - ML Service: Modelos y procesamiento
   - Config Service: Gestión centralizada
   - Comunicación entre servicios

3. **Infraestructura (90 min)**
   - Kubernetes: Pods, Services, Ingress
   - Base de datos PostgreSQL
   - Cache Redis
   - Storage MinIO

**Ejercicio Práctico:**
```bash
# Los participantes deben:
# 1. Identificar todos los pods del sistema
kubectl get pods -n traffic-system

# 2. Rastrear una request desde frontend hasta base de datos
kubectl logs -f deployment/traffic-system-backend -n traffic-system

# 3. Verificar comunicación entre servicios
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  curl http://traffic-system-ml-service:8001/health
```

**Evaluación:**
- Quiz de 20 preguntas sobre arquitectura
- Ejercicio práctico de trazabilidad de requests
- Presentación grupal de un componente

#### 2.2 Operaciones y Deployment

**Sesión 2: DevOps y CI/CD (6 horas)**

**Agenda:**
1. **Pipeline de CI/CD (120 min)**
   - GitHub Actions workflow
   - Proceso de build y testing
   - Deployment automático
   - Rollback procedures

2. **Gestión de Configuración (90 min)**
   - Helm charts y values
   - ConfigMaps y Secrets
   - Environment-specific configurations
   - Feature flags

3. **Monitoring y Logging (90 min)**
   - Prometheus metrics
   - Grafana dashboards
   - Log aggregation
   - Alerting rules

**Ejercicio Práctico:**
```bash
# 1. Simular deployment de nueva versión
git checkout -b feature/training-deployment
# Modificar imagen en values.yaml
helm upgrade training-system ./helm \
  --namespace training-environment \
  --values values-training.yaml

# 2. Configurar nueva métrica de Prometheus
cat >> prometheus-config.yaml << EOF
- job_name: 'training-metrics'
  static_configs:
  - targets: ['training-system:8000']
EOF

# 3. Crear nueva alerta
cat >> alerting-rules.yaml << EOF
- alert: TrainingSystemHighLatency
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: Training system experiencing high latency
EOF
```

#### 2.3 Troubleshooting y Debugging

**Sesión 3: Resolución de Problemas (8 horas)**

**Módulo 1: Debugging del Backend (2 horas)**
```python
# Herramientas de debugging en Django
# 1. Django Debug Toolbar
INSTALLED_APPS = [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# 2. Logging avanzado
import logging
logger = logging.getLogger(__name__)

def process_infraction(request):
    logger.info(f"Processing infraction for user {request.user.id}")
    try:
        # Process logic
        pass
    except Exception as e:
        logger.error(f"Failed to process infraction: {e}", exc_info=True)
        raise

# 3. Performance profiling
from django_extensions.management.commands import runprofileserver
# python manage.py runprofileserver 0.0.0.0:8000
```

**Módulo 2: Debugging del ML Service (2 horas)**
```python
# Herramientas de debugging para ML
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO

def debug_detection(image_path, model_path, save_debug=True):
    """Debug license plate detection step by step"""
    
    # Load image and model
    image = cv2.imread(image_path)
    model = YOLO(model_path)
    
    # Run detection
    results = model(image)
    
    if save_debug:
        # Save annotated image
        annotated = results[0].plot()
        cv2.imwrite(f"debug_{Path(image_path).stem}.jpg", annotated)
        
        # Print detection details
        for r in results:
            print(f"Detections: {len(r.boxes)}")
            for box in r.boxes:
                print(f"  Confidence: {box.conf.item():.3f}")
                print(f"  Coordinates: {box.xyxy.tolist()}")
    
    return results

# Monitoring GPU usage
import GPUtil
def monitor_gpu():
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        print(f"GPU {gpu.id}: {gpu.memoryUtil*100:.1f}% memory, {gpu.load*100:.1f}% load")
```

**Módulo 3: Troubleshooting de Infraestructura (2 horas)**
```bash
# Kubernetes troubleshooting toolkit

# 1. Pod debugging
kubectl describe pod <pod-name> -n traffic-system
kubectl logs <pod-name> -n traffic-system --previous
kubectl exec -it <pod-name> -n traffic-system -- /bin/bash

# 2. Network debugging
kubectl get svc,endpoints -n traffic-system
kubectl run netshoot --rm -i --tty --image=nicolaka/netshoot \
  -n traffic-system -- /bin/bash

# 3. Resource monitoring
kubectl top nodes
kubectl top pods -n traffic-system
kubectl get events -n traffic-system --sort-by='.lastTimestamp'

# 4. Storage debugging
kubectl get pv,pvc -n traffic-system
kubectl describe pvc <pvc-name> -n traffic-system
```

**Módulo 4: Performance Debugging (2 horas)**
```bash
# Database performance
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
  psql -U trafficuser -d trafficdb -c "
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"

# Redis performance
kubectl exec -it traffic-system-redis-master-0 -n traffic-system -- \
  redis-cli INFO memory

# Application profiling
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  python -m cProfile -o profile_output.prof manage.py shell
```

### Fase 3: Transferencia Operacional (Semanas 7-8)

#### 3.1 Procedimientos de Operación Diaria

**Sesión 4: Operaciones Rutinarias (4 horas)**

**Check-list Matutino:**
```bash
#!/bin/bash
# daily-health-check.sh

echo "=== Daily Health Check - $(date) ==="

# 1. Verificar estado de pods
echo "📊 Pod Status:"
kubectl get pods -n traffic-system | grep -v Running | head -10

# 2. Verificar métricas clave
echo "📈 Key Metrics:"
echo "  Backend Response Time: $(curl -s http://prometheus:9090/api/v1/query?query=histogram_quantile\(0.95,rate\(http_request_duration_seconds_bucket[5m]\)\) | jq -r '.data.result[0].value[1]') seconds"

echo "  ML Service Queue Length: $(curl -s http://prometheus:9090/api/v1/query?query=ml_processing_queue_length | jq -r '.data.result[0].value[1]')"

echo "  Database Connections: $(kubectl exec traffic-system-postgresql-0 -n traffic-system -- psql -U trafficuser -d trafficdb -t -c "SELECT count(*) FROM pg_stat_activity;")"

# 3. Verificar espacio en disco
echo "💾 Storage Usage:"
kubectl exec traffic-system-postgresql-0 -n traffic-system -- df -h /var/lib/postgresql/data

# 4. Verificar logs de errores
echo "🚨 Recent Errors:"
kubectl logs deployment/traffic-system-backend -n traffic-system --since=24h | grep ERROR | tail -5

# 5. Verificar backups
echo "💿 Backup Status:"
ls -la /backups/complete_* | tail -3

echo "=== Health Check Completed ==="
```

**Procedimientos de Respuesta a Alertas:**
```bash
# Alert Response Playbook

# 1. High Response Time Alert
alert_high_response_time() {
  echo "🚨 High response time detected"
  
  # Check current load
  kubectl top pods -n traffic-system
  
  # Check for slow queries
  kubectl exec traffic-system-postgresql-0 -n traffic-system -- \
    psql -U trafficuser -d trafficdb -c "
    SELECT query, mean_time, calls 
    FROM pg_stat_statements 
    WHERE mean_time > 1000 
    ORDER BY mean_time DESC 
    LIMIT 5;"
  
  # Scale if necessary
  current_replicas=$(kubectl get deployment traffic-system-backend -n traffic-system -o jsonpath='{.spec.replicas}')
  if [ "$current_replicas" -lt 5 ]; then
    kubectl scale deployment traffic-system-backend --replicas=$((current_replicas + 2)) -n traffic-system
    echo "Scaled backend to $((current_replicas + 2)) replicas"
  fi
}

# 2. Database Connection Alert
alert_db_connections() {
  echo "🚨 High database connections detected"
  
  # Check active connections
  kubectl exec traffic-system-postgresql-0 -n traffic-system -- \
    psql -U trafficuser -d trafficdb -c "
    SELECT 
      state, 
      count(*) 
    FROM pg_stat_activity 
    GROUP BY state;"
  
  # Kill long-running queries if necessary
  kubectl exec traffic-system-postgresql-0 -n traffic-system -- \
    psql -U trafficuser -d trafficdb -c "
    SELECT 
      pid, 
      state, 
      query_start, 
      left(query, 50) 
    FROM pg_stat_activity 
    WHERE state = 'active' 
    AND query_start < now() - interval '10 minutes';"
}
```

#### 3.2 Gestión de Incidentes

**Sesión 5: Manejo de Incidentes (6 horas)**

**Clasificación de Incidentes:**

| Prioridad | Tiempo de Respuesta | Tiempo de Resolución | Escalamiento |
|-----------|-------------------|---------------------|--------------|
| P1 (Crítico) | 15 minutos | 4 horas | Inmediato |
| P2 (Alto) | 1 hora | 24 horas | 2 horas |
| P3 (Medio) | 4 horas | 72 horas | 8 horas |
| P4 (Bajo) | 24 horas | 1 semana | No requerido |

**Simulacro de Incidente P1:**
```bash
# Scenario: Complete system outage
# Time: 09:00 AM (peak hours)
# Impact: All users unable to access system

# Step 1: Initial Response (0-5 minutes)
echo "📞 Incident declared at $(date)"
echo "📋 Creating incident ticket..."

# Step 2: Assessment (5-10 minutes)
kubectl get nodes  # Check cluster health
kubectl get pods -n traffic-system  # Check application health
kubectl get events -n traffic-system --sort-by='.lastTimestamp' | tail -20

# Step 3: Communication (10 minutes)
curl -X POST https://status-page.com/api/incidents \
  -H "Authorization: Bearer $STATUS_PAGE_TOKEN" \
  -d '{
    "name": "System Unavailable",
    "status": "investigating", 
    "message": "We are investigating reports of system unavailability.",
    "component_ids": ["system"]
  }'

# Step 4: Diagnosis and Resolution (10-30 minutes)
# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller --tail=50

# Check database connectivity
kubectl exec deployment/traffic-system-backend -n traffic-system -- \
  python manage.py check --database

# Step 5: Recovery Actions
# If database is down
kubectl delete pod traffic-system-postgresql-0 -n traffic-system

# If backend is down
kubectl rollout restart deployment/traffic-system-backend -n traffic-system

# Step 6: Verification (30-45 minutes)
curl -f https://traffic-system.domain.com/health/
curl -f https://traffic-system.domain.com/api/v1/infractions/ \
  -H "Authorization: Bearer $TEST_TOKEN"

# Step 7: Post-incident (45+ minutes)
# Update status page
curl -X PATCH https://status-page.com/api/incidents/$INCIDENT_ID \
  -H "Authorization: Bearer $STATUS_PAGE_TOKEN" \
  -d '{"status": "resolved", "message": "System is fully operational"}'

# Schedule post-mortem meeting
echo "📅 Post-mortem scheduled for $(date -d '+2 days')"
```

### Fase 4: Validación y Certificación (Semanas 9-10)

#### 4.1 Evaluaciones Prácticas

**Examen Práctico para Administradores:**
```bash
# Scenario: New ML model deployment
# Task: Deploy new model version without downtime
# Time limit: 2 hours

# 1. Download new model
wget https://models.company.com/license-plate-v2.1.pt -O /tmp/new-model.pt

# 2. Validate model locally
python validate_model.py /tmp/new-model.pt /tmp/test-images/

# 3. Update model in MinIO
kubectl exec deployment/traffic-system-minio -n traffic-system -- \
  mc cp /tmp/new-model.pt myminio/models/license-plate-detector.pt

# 4. Rolling restart of ML service
kubectl rollout restart deployment/traffic-system-ml-service -n traffic-system
kubectl rollout status deployment/traffic-system-ml-service -n traffic-system

# 5. Validate new model in production
curl -X POST http://ml-service:8001/detect/license-plates \
  -F "file=@/tmp/test-image.jpg" \
  -F "confidence_threshold=0.8"

# 6. Monitor for issues
kubectl logs deployment/traffic-system-ml-service -n traffic-system --tail=50
```

**Examen Práctico para Operadores:**
```bash
# Scenario: Performance degradation investigation
# Symptoms: Users reporting slow response times
# Task: Identify and resolve performance bottleneck
# Time limit: 1.5 hours

# 1. Initial assessment
kubectl top nodes
kubectl top pods -n traffic-system

# 2. Check application metrics
curl -s http://prometheus:9090/api/v1/query?query=rate\(http_requests_total[5m]\)
curl -s http://prometheus:9090/api/v1/query?query=histogram_quantile\(0.95,rate\(http_request_duration_seconds_bucket[5m]\)\)

# 3. Database analysis
kubectl exec traffic-system-postgresql-0 -n traffic-system -- \
  psql -U trafficuser -d trafficdb -c "
  SELECT 
    query,
    calls,
    total_time,
    mean_time
  FROM pg_stat_statements 
  ORDER BY total_time DESC 
  LIMIT 10;"

# 4. Identify bottleneck and implement solution
# (Could be: scale replicas, optimize query, clear cache, etc.)

# 5. Verify resolution
# Monitor metrics for improvement
```

#### 4.2 Certificación Final

**Criterios de Certificación:**

**Administradores:**
- [ ] Completar deployment de nueva versión sin downtime
- [ ] Resolver incidente P1 en tiempo objetivo
- [ ] Configurar nueva métrica y alerta de Prometheus
- [ ] Ejecutar backup completo y verificar integridad
- [ ] Documentar procedimiento nuevo en runbooks

**Operadores:**
- [ ] Identificar y resolver problema de performance
- [ ] Ejecutar procedimientos de mantenimiento rutinario
- [ ] Crear reporte de incidente siguiendo template
- [ ] Demostrar uso de herramientas de monitoreo
- [ ] Completar troubleshooting de conectividad

**Técnicos de Campo:**
- [ ] Usar interfaz de operador eficientemente
- [ ] Reportar incidente siguiendo procedimientos
- [ ] Interpretar dashboards de monitoreo básicos
- [ ] Ejecutar validaciones de campo
- [ ] Documentar observaciones apropiadamente

## 📚 Documentación de Soporte

### 4.3 Biblioteca de Recursos

**Documentación Técnica:**
- [📖 Arquitectura del Sistema](../architecture/overview.md)
- [🔧 API Documentation](../api/backend-api.md)
- [🚀 Deployment Guide](../deployment/kubernetes-guide.md)
- [📊 Monitoring Guide](../operations/monitoring-guide.md)
- [🔍 Troubleshooting Guide](../operations/troubleshooting-guide.md)

**Runbooks Operacionales:**
- [🚨 Emergency Procedures](./runbooks.md#emergencias)
- [🔧 Maintenance Procedures](./runbooks.md#mantenimiento)
- [📊 Monitoring Procedures](./runbooks.md#monitoreo)
- [🔐 Security Procedures](./runbooks.md#seguridad)

**Videos de Entrenamiento:**
- Sistema Overview (30 min)
- Database Management (45 min)
- Kubernetes Operations (60 min)
- Incident Response (40 min)
- Performance Tuning (50 min)

### 4.4 Herramientas de Soporte

**Acceso a Sistemas:**
```bash
# Production environment (read-only for learning)
kubectl config use-context production-readonly

# Training environment (full access)
kubectl config use-context training-full

# Development environment
kubectl config use-context development
```

**Dashboards de Monitoreo:**
- [Production Dashboard](https://grafana.company.com/d/traffic-system-prod)
- [Training Dashboard](https://grafana-training.company.com/d/traffic-system-training)
- [Infrastructure Dashboard](https://grafana.company.com/d/infrastructure)

**Herramientas de Comunicación:**
- Slack: #traffic-system-ops
- Email: traffic-system-support@company.com
- Emergency Phone: +1-800-TRAFFIC

## 📈 Métricas de Éxito

### Indicadores de Transferencia Exitosa

**Métricas Técnicas:**
- ✅ 95% de uptime durante primer mes post-transferencia
- ✅ Tiempo promedio de resolución de incidentes < 30 min
- ✅ 0 escalamientos no planificados en primeras 2 semanas
- ✅ 100% de backups exitosos sin intervención externa

**Métricas de Conocimiento:**
- ✅ 90% aprobación en exámenes de certificación
- ✅ 100% del personal operativo certificado
- ✅ 5 procedimientos documentados por el equipo interno
- ✅ 0 dependencias críticas de consultores externos

**Métricas de Proceso:**
- ✅ Tiempo de respuesta a incidentes dentro de SLA
- ✅ Documentación actualizada mensualmente
- ✅ Proceso de mejora continua establecido
- ✅ Plan de capacitación continua implementado

## 🔄 Proceso de Mejora Continua

### Post-Transferencia

**Revisiones Periódicas:**
- **Semanal (primeras 4 semanas)**: Revisión operacional
- **Mensual (primeros 6 meses)**: Evaluación de procesos
- **Trimestral**: Actualización de documentación
- **Semestral**: Evaluación de competencias

**Retroalimentación Continua:**
```bash
# Implementar métricas de conocimiento
kubectl apply -f - << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: knowledge-metrics
  namespace: traffic-system
data:
  incident_resolution_time.json: |
    {
      "target": 30,
      "measurement": "minutes",
      "frequency": "per_incident"
    }
  documentation_updates.json: |
    {
      "target": 1,
      "measurement": "updates",
      "frequency": "per_month"
    }
EOF
```

**Programa de Mentoría:**
- Sesiones mensuales con expertos externos
- Revisión de casos complejos
- Actualización en nuevas tecnologías
- Intercambio de experiencias con otros equipos

---

**Contactos para Transferencia de Conocimiento:**
- **Technical Lead**: tech-lead@company.com
- **Operations Manager**: ops-manager@company.com
- **Training Coordinator**: training@company.com
- **Emergency Support**: support@company.com (24/7)

**Cronograma de Seguimiento:**
- Semana 11: Revisión post-transferencia
- Semana 15: Evaluación de autonomía
- Mes 3: Certificación de independencia operacional
- Mes 6: Evaluación final y cierre del proyecto