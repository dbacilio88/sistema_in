#!/bin/bash

# Script para configurar HTTPS en AWS con Docker Compose
echo "🔒 Configurando HTTPS para AWS..."

# Variables
DOMAIN=${1:-54.86.67.166}
SSL_DIR="./ssl"

# Crear directorio SSL si no existe
mkdir -p $SSL_DIR

# Función para generar certificado autofirmado
generate_self_signed() {
    echo "📜 Generando certificado SSL autofirmado para $DOMAIN..."
    
    openssl req -x509 -newkey rsa:4096 \
        -keyout $SSL_DIR/key.pem \
        -out $SSL_DIR/cert.pem \
        -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=$DOMAIN"
    
    if [ $? -eq 0 ]; then
        echo "✅ Certificado SSL generado exitosamente"
        chmod 600 $SSL_DIR/key.pem
        chmod 644 $SSL_DIR/cert.pem
    else
        echo "❌ Error generando certificado SSL"
        exit 1
    fi
}

# Función para configurar Let's Encrypt (producción)
setup_letsencrypt() {
    echo "📜 Configurando Let's Encrypt para $DOMAIN..."
    
    # Verificar si certbot está instalado
    if ! command -v certbot &> /dev/null; then
        echo "🔧 Instalando certbot..."
        apt-get update && apt-get install -y certbot
    fi
    
    # Generar certificado
    certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email admin@$DOMAIN \
        -d $DOMAIN
    
    if [ $? -eq 0 ]; then
        echo "✅ Certificado Let's Encrypt generado"
        # Copiar certificados al directorio local
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/cert.pem
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/key.pem
        chmod 600 $SSL_DIR/key.pem
        chmod 644 $SSL_DIR/cert.pem
    else
        echo "⚠️ Error con Let's Encrypt, usando certificado autofirmado..."
        generate_self_signed
    fi
}

# Verificar argumentos
echo "🌐 Configurando SSL para dominio: $DOMAIN"

if [ "$2" == "production" ]; then
    echo "🚀 Modo producción - intentando usar Let's Encrypt"
    setup_letsencrypt
else
    echo "🔧 Modo desarrollo - usando certificado autofirmado"
    generate_self_signed
fi

# Verificar que los archivos existan
if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
    echo ""
    echo "✅ Configuración SSL completada"
    echo "   📁 Certificados en: $SSL_DIR/"
    echo "   📜 cert.pem: $(ls -lh $SSL_DIR/cert.pem | awk '{print $5}')"
    echo "   🔑 key.pem: $(ls -lh $SSL_DIR/key.pem | awk '{print $5}')"
    echo ""
    echo "🚀 Para iniciar con HTTPS:"
    echo "   docker-compose -f docker-compose.yml -f docker-compose.aws.yml --env-file .env.aws up -d"
    echo ""
    echo "🌐 URLs disponibles:"
    echo "   • HTTP:  http://$DOMAIN"
    echo "   • HTTPS: https://$DOMAIN"
    echo "   • API:   https://$DOMAIN/api/"
    echo "   • ML:    https://$DOMAIN/ml/"
else
    echo "❌ Error: No se pudieron generar los certificados SSL"
    exit 1
fi