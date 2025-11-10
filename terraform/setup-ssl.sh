#!/bin/bash

# Configuración SSL para Sistema IN
# Este script configura certificados SSL usando Let's Encrypt

set -e

echo "🔒 Configurando SSL para Sistema IN..."

# Variables (editar antes de ejecutar)
DOMAIN="your-domain.com"  # Cambiar por tu dominio
EMAIL="your-email@domain.com"  # Cambiar por tu email

# Verificar que el dominio esté configurado
if [ "$DOMAIN" = "your-domain.com" ]; then
    echo "❌ Error: Debes configurar tu dominio en la variable DOMAIN"
    echo "Edita este script y cambia 'your-domain.com' por tu dominio real"
    exit 1
fi

if [ "$EMAIL" = "your-email@domain.com" ]; then
    echo "❌ Error: Debes configurar tu email en la variable EMAIL"
    echo "Edita este script y cambia 'your-email@domain.com' por tu email real"
    exit 1
fi

echo "📋 Configurando SSL para: $DOMAIN"
echo "📧 Email de contacto: $EMAIL"

# Crear directorio nginx si no existe
mkdir -p nginx/conf.d
mkdir -p nginx/ssl

# Actualizar configuración de nginx con el dominio real
echo "⚙️ Actualizando configuración de Nginx..."
sed -i "s/your-domain.com/$DOMAIN/g" nginx/conf.d/default.conf

# Actualizar docker-compose con el dominio y email
echo "⚙️ Actualizando Docker Compose..."
sed -i "s/your-domain.com/$DOMAIN/g" docker-compose.ssl.yml
sed -i "s/your-email@domain.com/$EMAIL/g" docker-compose.ssl.yml

# Crear certificado temporal para primera ejecución
echo "🔑 Creando certificado temporal..."
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 1 -newkey rsa:2048 \
    -keyout nginx/ssl/temp.key \
    -out nginx/ssl/temp.crt \
    -subj "/CN=$DOMAIN"

# Iniciar Nginx con certificado temporal
echo "🚀 Iniciando Nginx con certificado temporal..."
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d nginx

# Esperar a que Nginx esté listo
echo "⏳ Esperando a que Nginx esté listo..."
sleep 10

# Obtener certificado real de Let's Encrypt
echo "🔒 Obteniendo certificado SSL de Let's Encrypt..."
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml run --rm certbot \
    certonly --webroot --webroot-path=/var/www/certbot \
    --email $EMAIL --agree-tos --no-eff-email \
    -d $DOMAIN

# Actualizar configuración para usar certificados reales
echo "⚙️ Actualizando configuración para certificados reales..."
cat > nginx/conf.d/default.conf << EOF
# Default HTTP server (redirects to HTTPS)
server {
    listen 80;
    server_name $DOMAIN;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

# HTTPS server for Frontend
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # Frontend (React app)
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Rate limiting
        limit_req zone=frontend burst=20 nodelay;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Rate limiting for API
        limit_req zone=api burst=10 nodelay;
    }

    # ML Service
    location /ml/ {
        proxy_pass http://ml-service:8001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Longer timeout for ML processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Dashboard
    location /dashboard/ {
        proxy_pass http://frontend-dashboard:3001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Reiniciar Nginx con la nueva configuración
echo "🔄 Reiniciando Nginx con certificados SSL..."
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml restart nginx

# Configurar renovación automática
echo "🔄 Configurando renovación automática..."
cat > renew-ssl.sh << 'EOF'
#!/bin/bash
# Script para renovar certificados SSL automáticamente

echo "🔄 Renovando certificados SSL..."
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml run --rm certbot renew

echo "🔄 Reiniciando Nginx..."
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml restart nginx

echo "✅ Renovación completada"
EOF

chmod +x renew-ssl.sh

# Crear cron job para renovación automática (ejecutar cada 2 meses)
echo "⏰ Configurando cron job para renovación automática..."
(crontab -l 2>/dev/null; echo "0 3 1 */2 * cd $(pwd) && ./renew-ssl.sh >> ssl-renew.log 2>&1") | crontab -

echo ""
echo "✅ Configuración SSL completada!"
echo ""
echo "🌐 Tu sitio ahora está disponible en:"
echo "   https://$DOMAIN"
echo ""
echo "🔒 Certificado SSL válido por 90 días"
echo "🔄 Renovación automática configurada cada 2 meses"
echo ""
echo "📋 Comandos útiles:"
echo "   - Verificar certificado: openssl s_client -connect $DOMAIN:443 -servername $DOMAIN"
echo "   - Renovar manualmente: ./renew-ssl.sh"
echo "   - Ver logs de renovación: tail -f ssl-renew.log"