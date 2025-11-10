#!/bin/bash

# Script para configurar HTTPS en desarrollo
echo "🔒 Configurando HTTPS para desarrollo..."

# Crear directorio para certificados si no existe
mkdir -p ./ssl

# Generar certificado SSL autofirmado
if [ ! -f "./ssl/cert.pem" ] || [ ! -f "./ssl/key.pem" ]; then
    echo "📜 Generando certificado SSL autofirmado..."
    
    openssl req -x509 -newkey rsa:4096 -keyout ./ssl/key.pem -out ./ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"
    
    if [ $? -eq 0 ]; then
        echo "✅ Certificado SSL generado exitosamente"
        echo "   - Certificado: ./ssl/cert.pem"
        echo "   - Llave privada: ./ssl/key.pem"
    else
        echo "❌ Error generando certificado SSL"
        exit 1
    fi
else
    echo "📜 Certificados SSL ya existen"
fi

echo ""
echo "🚀 Para usar HTTPS en desarrollo:"
echo "   1. cd frontend-dashboard"
echo "   2. npm run dev:https"
echo "   3. Acepta el certificado autofirmado en el navegador"
echo "   4. Accede a: https://localhost:3000"
echo ""
echo "⚠️  NOTA: Los navegadores mostrarán una advertencia de seguridad."
echo "    Esto es normal para certificados autofirmados en desarrollo."
echo "    Haz clic en 'Avanzado' -> 'Continuar a localhost'"