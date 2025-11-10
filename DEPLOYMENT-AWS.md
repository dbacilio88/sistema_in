# 🚀 Sistema IN - AWS Deployment Guide

## Resumen

Se ha creado una infraestructura simple pero completa para desplegar tu sistema de detección de infracciones de tránsito en AWS usando:

- **1 Instancia EC2** t3.xlarge (4 vCPUs, 16GB RAM)
- **Docker Compose** para ejecutar todos los servicios
- **Terraform** para gestionar la infraestructura
- **GitHub Actions** para CI/CD automático

## 📁 Estructura Creada

```
sistema_in/
├── terraform/                     # Infraestructura como código
│   ├── main.tf                   # Configuración principal
│   ├── variables.tf              # Variables
│   ├── outputs.tf                # Salidas
│   ├── user-data.sh              # Script de configuración EC2
│   ├── terraform.tfvars.example  # Ejemplo de variables
│   └── README.md                 # Documentación Terraform
├── .github/workflows/            # Pipelines CI/CD
│   ├── infrastructure.yml        # Deploy infraestructura
│   └── deploy.yml                # Deploy aplicación
└── DEPLOYMENT-AWS.md             # Esta documentación
```

## 🏗️ Arquitectura Simplificada

```
Internet
    ↓
[Elastic IP] → [EC2 t3.xlarge]
                    ↓
    [Docker Compose con todos los servicios]
    ├── Django (puerto 8000)
    ├── FastAPI Inference (puerto 8001)  
    ├── Frontend React (puerto 3002)
    ├── PostgreSQL (puerto 5432)
    ├── Redis (puerto 6379)
    ├── RabbitMQ (puertos 5672, 15672)
    ├── MinIO (puertos 9000, 9001)
    ├── Prometheus (puerto 9090)
    └── Grafana (puerto 3001)
```

## 🚀 Guía de Despliegue

### Paso 1: Configurar Secretos en GitHub

Ve a tu repositorio → Settings → Secrets and variables → Actions y agrega:

```
AWS_ACCESS_KEY_ID: tu_access_key
AWS_SECRET_ACCESS_KEY: tu_secret_key
AWS_KEY_PAIR_NAME: nombre-de-tu-key-pair (opcional)
```

### Paso 2: Desplegar Infraestructura

1. **Opción A: GitHub Actions (Recomendado)**
   - Ve a Actions → "Infrastructure - Deploy to AWS"
   - Run workflow → Selecciona "apply"

2. **Opción B: Terraform Manual**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edita terraform.tfvars
   terraform init
   terraform plan
   terraform apply
   ```

### Paso 3: Desplegar Aplicación

Una vez que la infraestructura esté lista:

1. **GitHub Actions automático**: Push a `main` o `master`
2. **Manual**: SSH a la instancia y ejecutar `/opt/sistema-in/deploy.sh`

## 📊 URLs de Acceso

Después del despliegue, tu aplicación estará disponible en:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://`<IP>`:3002 | Dashboard principal |
| Django API | http://`<IP>`:8000 | API REST |
| Django Admin | http://`<IP>`:8000/admin/ | Panel de administración |
| Inference API | http://`<IP>`:8001 | Servicio de ML |
| RabbitMQ | http://`<IP>`:15672 | Gestión de colas |
| MinIO | http://`<IP>`:9001 | Almacenamiento |
| Grafana | http://`<IP>`:3001 | Dashboards |
| Prometheus | http://`<IP>`:9090 | Métricas |

## 🔧 Gestión Post-Despliegue

### Conectar a la Instancia

```bash
# Con key pair
ssh -i ~/.ssh/tu-key.pem ec2-user@<IP>

# Con AWS Session Manager (sin key pair)
aws ssm start-session --target <instance-id>
```

### Scripts de Gestión

En `/opt/sistema-in/`:

```bash
./deploy.sh     # Redesplegar aplicación
./monitor.sh    # Ver estado del sistema
./restart.sh    # Reiniciar servicios
./logs.sh <service>  # Ver logs específicos
```

### Comandos Útiles

```bash
# Ver servicios
docker-compose ps

# Ver logs
docker-compose logs -f django
docker-compose logs -f inference

# Reiniciar servicio específico
docker-compose restart django

# Ver recursos del sistema
htop
./monitor.sh
```

## 💰 Costos Estimados

| Instancia | Costo/mes (On-Demand) | Costo/mes (Reserved) |
|-----------|----------------------|---------------------|
| t3.xlarge | ~$150 | ~$95 |

**Optimización de costos:**
- Usa Spot Instances para desarrollo (~$45-75/mes)
- Considera Reserved Instances para producción
- Para desarrollo, puedes usar t3.large (~$75/mes)

## 🔒 Seguridad

⚠️ **Configuración actual**: Todos los puertos están abiertos a internet para facilitar el desarrollo.

**Para producción, considera:**

1. **Restringir acceso por IP**:
   ```hcl
   # En terraform/main.tf, cambiar:
   cidr_blocks = ["0.0.0.0/0"]
   # Por:
   cidr_blocks = ["tu.ip.específica/32"]
   ```

2. **Load Balancer con SSL**
3. **AWS Secrets Manager** para credenciales
4. **Backup automático**

## 🚨 Solución de Problemas

### Infraestructura no se despliega
```bash
# Verificar credenciales AWS
aws sts get-caller-identity

# Verificar Terraform
cd terraform
terraform validate
terraform plan
```

### Aplicación no accesible
```bash
# Conectar a la instancia
ssh -i key.pem ec2-user@<IP>

# Verificar servicios
cd /opt/sistema-in
./monitor.sh
docker-compose ps

# Ver logs
./logs.sh django
./logs.sh inference
```

### Servicios no inician
```bash
# Verificar recursos
free -h
df -h

# Revisar Docker
sudo systemctl status docker
docker-compose down
docker-compose up -d
```

## 🔄 CI/CD Pipeline

### Trigger automático
- Push a `main` o `master` → Deploy automático
- Cambios en `/terraform/` → Update infraestructura

### Manual
- Actions → "Infrastructure" → Run workflow
- Actions → "Deploy to AWS EC2" → Run workflow

## 📈 Monitoreo

- **CloudWatch**: Métricas básicas del sistema
- **Grafana**: http://`<IP>`:3001 (admin/admin)
- **Prometheus**: http://`<IP>`:9090
- **Logs**: `/opt/sistema-in/logs.sh <service>`

## 🧹 Limpieza

Para eliminar toda la infraestructura:

```bash
cd terraform
terraform destroy
```

O desde GitHub Actions: Infrastructure → Run workflow → destroy

## 📞 Soporte

Para problemas comunes:

1. **Revisar logs de GitHub Actions**
2. **Verificar outputs de Terraform**
3. **Conectar a la instancia y revisar `/opt/sistema-in/README-DEPLOYMENT.md`**
4. **Usar scripts de monitoreo incluidos**

---

## 🎉 ¡Listo!

Tu sistema de detección de infracciones está ahora configurado para desplegarse automáticamente en AWS. Solo necesitas hacer push a tu repositorio y GitHub Actions se encargará del resto.

**Próximos pasos:**
1. Configurar los secretos de GitHub
2. Hacer push para activar el pipeline
3. Acceder a tu aplicación en las URLs proporcionadas
4. Configurar usuarios y datos iniciales en Django Admin