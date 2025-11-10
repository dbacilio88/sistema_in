# 🔒 Configuración SSL/HTTPS para Sistema IN

Esta guía te ayudará a configurar certificados SSL automáticos usando Let's Encrypt para tener HTTPS en tu aplicación.

## 📋 Requisitos previos

1. **Dominio configurado**: Necesitas un dominio que apunte a la IP pública de tu instancia EC2
2. **DNS configurado**: Asegúrate de que tu dominio resuelva correctamente a la IP de tu servidor
3. **Aplicación funcionando**: La aplicación debe estar ejecutándose correctamente en HTTP primero

## 🚀 Configuración paso a paso

### 1. Configurar tu dominio

Antes de empezar, asegúrate de que tu dominio esté configurado:

```bash
# Verificar que tu dominio apunte a la IP correcta
nslookup tu-dominio.com
```

### 2. Preparar archivos SSL

Los archivos necesarios ya están incluidos en el repositorio:

- `docker-compose.ssl.yml` - Configuración de Docker Compose con SSL
- `nginx/nginx.conf` - Configuración principal de Nginx
- `nginx/conf.d/default.conf` - Configuración del virtual host
- `setup-ssl.sh` - Script de configuración automática

### 3. Configurar SSL

```bash
# Ir al directorio de la aplicación
cd /opt/sistema-in

# Copiar archivos SSL del repositorio si no están presentes
cp terraform/docker-compose.ssl.yml .
cp -r terraform/nginx .
cp terraform/setup-ssl.sh .

# Hacer el script ejecutable
chmod +x setup-ssl.sh

# Editar el script con tu dominio y email
nano setup-ssl.sh
```

**Edita estas líneas en `setup-ssl.sh`:**
```bash
DOMAIN="tu-dominio.com"        # Cambiar por tu dominio real
EMAIL="tu-email@dominio.com"   # Cambiar por tu email real
```

### 4. Ejecutar configuración SSL

```bash
# Ejecutar el script de configuración
./setup-ssl.sh
```

El script realizará automáticamente:
- ✅ Configuración de Nginx con proxy reverso
- ✅ Obtención de certificados SSL de Let's Encrypt
- ✅ Configuración de redirección HTTP → HTTPS
- ✅ Configuración de renovación automática

### 5. Deployment con SSL

Una vez configurado SSL, usa el script de deployment específico:

```bash
# Deployment con SSL habilitado
./deploy-ssl.sh
```

## 🌐 URLs disponibles

Después de la configuración SSL, tu aplicación estará disponible en:

- **Frontend**: `https://tu-dominio.com`
- **API Backend**: `https://tu-dominio.com/api/`
- **ML Service**: `https://tu-dominio.com/ml/`
- **Dashboard**: `https://tu-dominio.com/dashboard/`

## 🔄 Renovación automática

El certificado SSL se renovará automáticamente cada 2 meses mediante un cron job.

### Comandos útiles para SSL:

```bash
# Verificar certificado
openssl s_client -connect tu-dominio.com:443 -servername tu-dominio.com

# Renovar certificado manualmente
./renew-ssl.sh

# Ver logs de renovación
tail -f ssl-renew.log

# Verificar estado de Nginx
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml ps nginx

# Ver logs de Nginx
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml logs nginx
```

## 🛡️ Características de seguridad incluidas

- **Certificados SSL/TLS automáticos** con Let's Encrypt
- **Redirección HTTP → HTTPS** automática
- **Rate limiting** para proteger contra ataques
- **Headers de seguridad** (HSTS, XSS Protection, etc.)
- **Proxy reverso** con Nginx para mejor rendimiento
- **Renovación automática** de certificados

## 🚨 Solución de problemas

### Error: Dominio no resuelve
```bash
# Verificar DNS
nslookup tu-dominio.com
dig tu-dominio.com
```

### Error: Puerto 80/443 no accesible
```bash
# Verificar security groups en AWS
# Asegurar que los puertos 80 y 443 estén abiertos
```

### Error: Certificado no se puede obtener
```bash
# Verificar que Nginx esté funcionando
docker-compose ps nginx

# Verificar logs de certbot
docker-compose logs certbot
```

### Regenerar certificados
```bash
# Eliminar certificados existentes
docker volume rm $(docker volume ls -q | grep certbot)

# Ejecutar setup-ssl.sh nuevamente
./setup-ssl.sh
```

## 📚 Estructura de archivos SSL

```
/opt/sistema-in/
├── docker-compose.yml          # Configuración base
├── docker-compose.ssl.yml      # Configuración SSL adicional
├── nginx/
│   ├── nginx.conf             # Configuración principal de Nginx
│   └── conf.d/
│       └── default.conf       # Virtual host con SSL
├── setup-ssl.sh               # Script de configuración
├── deploy-ssl.sh              # Script de deployment con SSL
└── renew-ssl.sh               # Script de renovación
```

¡Tu aplicación ahora tendrá HTTPS seguro y profesional! 🔒✨