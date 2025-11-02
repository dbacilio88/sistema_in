# Guía de Despliegue del Sistema de Detección de Infracciones de Tráfico

## Requisitos Previos

### Herramientas Necesarias
- Docker y Docker Compose
- Kubernetes cluster (v1.24+)
- Helm (v3.8+)
- kubectl configurado
- Terraform (v1.0+) - opcional para infraestructura

### Recursos Mínimos
- **Desarrollo**: 8GB RAM, 4 vCPUs, 50GB almacenamiento
- **Staging**: 16GB RAM, 8 vCPUs, 200GB almacenamiento  
- **Producción**: 64GB RAM, 32 vCPUs, 1TB almacenamiento

## Despliegue con Docker Compose (Desarrollo)

### 1. Preparación del Entorno
```bash
# Clonar el repositorio
git clone <repository-url>
cd sistema_in

# Crear archivos de configuración
cp .env.example .env
# Editar .env con las configuraciones necesarias
```

### 2. Construcción y Despliegue
```bash
# Construir e iniciar todos los servicios
docker-compose up -d

# Verificar estado de los servicios
docker-compose ps

# Ver logs
docker-compose logs -f
```

### 3. Inicialización de la Base de Datos
```bash
# Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser

# Cargar datos de prueba (opcional)
docker-compose exec backend python manage.py loaddata fixtures/sample_data.json
```

## Despliegue en Kubernetes

### 1. Preparación del Cluster

#### Usando Terraform (Recomendado)

**AWS EKS:**
```bash
cd deployment/terraform

# Configurar variables
cp terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars

# Inicializar y aplicar
terraform init
terraform plan
terraform apply
```

**Azure AKS:**
```bash
cd deployment/terraform/azure

# Configurar variables
export TF_VAR_project_id="your-project-id"
export TF_VAR_environment="production"

# Desplegar
terraform init
terraform plan
terraform apply
```

**Google GKE:**
```bash
cd deployment/terraform/gcp

# Configurar variables
export TF_VAR_project_id="your-project-id"
export TF_VAR_environment="production"

# Desplegar
terraform init
terraform plan
terraform apply
```

#### Configuración Manual de Kubernetes

Si no usas Terraform, configura manualmente:

```bash
# Crear namespace
kubectl create namespace traffic-system

# Instalar NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx

# Instalar cert-manager para TLS
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

### 2. Despliegue con Helm

#### Configuración de Repositorios
```bash
# Agregar repositorios de dependencias
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

#### Instalación para Desarrollo
```bash
cd deployment/helm

# Instalar con configuración de desarrollo
helm install traffic-system . \
  --namespace traffic-system \
  --create-namespace \
  -f values-development.yaml
```

#### Instalación para Producción
```bash
cd deployment/helm

# Crear secrets para producción
kubectl create secret generic traffic-system-secrets \
  --namespace traffic-system \
  --from-literal=postgres-password="<secure-password>" \
  --from-literal=redis-password="<secure-password>" \
  --from-literal=secret-key="<django-secret-key>"

# Instalar con configuración de producción
helm install traffic-system . \
  --namespace traffic-system \
  --create-namespace \
  -f values-production.yaml \
  --set postgresql.auth.postgresPassword="<postgres-password>" \
  --set redis.auth.password="<redis-password>"
```

### 3. Verificación del Despliegue

```bash
# Verificar pods
kubectl get pods -n traffic-system

# Verificar servicios
kubectl get services -n traffic-system

# Verificar ingress
kubectl get ingress -n traffic-system

# Ver logs de un servicio
kubectl logs -f deployment/traffic-system-backend -n traffic-system
```

## Configuración de Red y Dominio

### 1. Configuración de DNS
```bash
# Obtener IP externa del Load Balancer
kubectl get service ingress-nginx-controller -o wide

# Configurar DNS record
# traffic-system.yourdomain.com -> EXTERNAL-IP
```

### 2. Configuración de TLS
```bash
# Aplicar ClusterIssuer para Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Configuración de Monitoreo

### 1. Acceso a Grafana
```bash
# Obtener password de Grafana
kubectl get secret traffic-system-grafana \
  -n traffic-system \
  -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward para acceso local
kubectl port-forward service/traffic-system-grafana 3000:80 -n traffic-system
```

### 2. Configuración de Alertas
```bash
# Configurar Slack notifications (ejemplo)
kubectl create secret generic alertmanager-slack \
  --namespace traffic-system \
  --from-literal=webhook-url="https://hooks.slack.com/your-webhook"
```

## Configuración de Backups

### 1. Backup de Base de Datos
```bash
# Crear CronJob para backups automáticos
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: traffic-system
spec:
  schedule: "0 2 * * *"  # Diario a las 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h traffic-system-postgresql -U trafficuser trafficdb > /backup/backup-$(date +%Y%m%d-%H%M%S).sql
              # Upload to S3/Azure/GCS
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: traffic-system-postgresql
                  key: password
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
EOF
```

## Escalamiento y Optimización

### 1. Escalamiento Horizontal
```bash
# Escalar manualmente
kubectl scale deployment traffic-system-backend --replicas=5 -n traffic-system

# Configurar HPA (incluido en Helm chart)
kubectl get hpa -n traffic-system
```

### 2. Escalamiento Vertical
```bash
# Actualizar recursos con Helm
helm upgrade traffic-system . \
  --namespace traffic-system \
  --set backend.resources.requests.cpu=2000m \
  --set backend.resources.requests.memory=2Gi
```

## Troubleshooting

### 1. Problemas Comunes

**Pods en estado Pending:**
```bash
# Verificar recursos disponibles
kubectl describe nodes
kubectl top nodes

# Verificar PVCs
kubectl get pvc -n traffic-system
```

**Problemas de Red:**
```bash
# Verificar Network Policies
kubectl get networkpolicy -n traffic-system

# Probar conectividad
kubectl run test-pod --image=busybox -it --rm -- /bin/sh
nslookup traffic-system-backend.traffic-system.svc.cluster.local
```

**Problemas de Base de Datos:**
```bash
# Verificar estado de PostgreSQL
kubectl logs deployment/traffic-system-postgresql -n traffic-system

# Conectar a la base de datos
kubectl exec -it deployment/traffic-system-postgresql -n traffic-system -- psql -U trafficuser -d trafficdb
```

### 2. Logs y Debugging
```bash
# Ver todos los logs del namespace
kubectl logs -f -l app.kubernetes.io/name=traffic-system -n traffic-system

# Debugear pod específico
kubectl describe pod <pod-name> -n traffic-system
kubectl exec -it <pod-name> -n traffic-system -- /bin/bash
```

## Actualizaciones

### 1. Actualización de la Aplicación
```bash
# Actualizar imágenes
helm upgrade traffic-system . \
  --namespace traffic-system \
  --set images.backend.tag=v1.1.0 \
  --set images.mlService.tag=v1.1.0

# Verificar rollout
kubectl rollout status deployment/traffic-system-backend -n traffic-system
```

### 2. Rollback
```bash
# Ver historial de releases
helm history traffic-system -n traffic-system

# Hacer rollback
helm rollback traffic-system 1 -n traffic-system
```

## Mantenimiento

### 1. Limpieza de Recursos
```bash
# Limpiar imágenes no utilizadas
kubectl delete pod $(kubectl get pods -n traffic-system | grep Evicted | awk '{print $1}') -n traffic-system

# Limpiar PVCs huérfanos
kubectl get pvc -n traffic-system | grep Released
```

### 2. Actualizaciones de Seguridad
```bash
# Actualizar nodos del cluster (depende del proveedor)
# AWS EKS: usar terraform apply con nueva versión
# Azure AKS: az aks upgrade
# Google GKE: gcloud container clusters upgrade
```

## Scripts de Automatización

Consulta los scripts en `deployment/scripts/` para automatización de tareas comunes:
- `deploy.sh`: Despliegue automatizado
- `backup.sh`: Backup de base de datos
- `monitor.sh`: Verificación de salud del sistema
- `scale.sh`: Escalamiento automatizado

Para más información detallada, consulta la documentación específica de cada componente en el directorio `docs/`.