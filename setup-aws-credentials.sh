#!/bin/bash

# Script para configurar credenciales AWS para desarrollo local
# Ejecutar: source ./setup-aws-credentials.sh

echo "🔐 Configurando credenciales AWS para Sistema IN..."

# Verificar si AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI no está instalado. Instalando..."
    
    # Para Ubuntu/Debian
    if command -v apt &> /dev/null; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    
    # Para macOS
    elif command -v brew &> /dev/null; then
        brew install awscli
    
    # Para Windows (WSL)
    else
        echo "Por favor, instala AWS CLI manualmente: https://aws.amazon.com/cli/"
        exit 1
    fi
fi

echo "✅ AWS CLI instalado correctamente"

# Configurar credenciales
echo ""
echo "📝 Configurando credenciales AWS..."
echo "Necesitarás:"
echo "1. AWS Access Key ID"
echo "2. AWS Secret Access Key" 
echo "3. Región por defecto (recomendado: us-east-1)"
echo ""

read -p "¿Quieres configurar las credenciales ahora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Configurar perfil específico para el proyecto
    echo "Configurando perfil 'sistema-in'..."
    aws configure --profile sistema-in
    
    # Exportar el perfil para la sesión actual
    export AWS_PROFILE=sistema-in
    
    echo ""
    echo "✅ Credenciales configuradas!"
    echo "📋 Para usar este perfil en el futuro, ejecuta:"
    echo "   export AWS_PROFILE=sistema-in"
    
    # Agregar al bashrc/zshrc
    read -p "¿Quieres agregar AWS_PROFILE=sistema-in a tu shell profile? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f ~/.bashrc ]; then
            echo "export AWS_PROFILE=sistema-in" >> ~/.bashrc
            echo "✅ Agregado a ~/.bashrc"
        fi
        if [ -f ~/.zshrc ]; then
            echo "export AWS_PROFILE=sistema-in" >> ~/.zshrc
            echo "✅ Agregado a ~/.zshrc"
        fi
    fi
    
else
    echo "⚠️ Credenciales no configuradas."
    echo "Puedes configurarlas más tarde con: aws configure --profile sistema-in"
fi

# Verificar credenciales
echo ""
echo "🔍 Verificando credenciales..."

if aws sts get-caller-identity --profile sistema-in &> /dev/null; then
    echo "✅ Credenciales AWS válidas"
    
    # Mostrar información de la cuenta
    echo ""
    echo "📊 Información de la cuenta AWS:"
    aws sts get-caller-identity --profile sistema-in --output table
    
else
    echo "❌ Las credenciales no son válidas o no están configuradas"
    echo "💡 Ejecuta: aws configure --profile sistema-in"
fi

# Verificar permisos necesarios
echo ""
echo "🔐 Verificando permisos..."

# Lista de servicios que necesitamos verificar
services=("ec2" "iam" "vpc" "logs")

for service in "${services[@]}"; do
    case $service in
        "ec2")
            if aws ec2 describe-regions --profile sistema-in &> /dev/null; then
                echo "✅ Permisos EC2: OK"
            else
                echo "❌ Permisos EC2: Faltantes"
            fi
            ;;
        "iam")
            if aws iam get-user --profile sistema-in &> /dev/null; then
                echo "✅ Permisos IAM: OK"
            else
                echo "⚠️ Permisos IAM: Limitados (puede funcionar con roles)"
            fi
            ;;
        "vpc")
            if aws ec2 describe-vpcs --profile sistema-in &> /dev/null; then
                echo "✅ Permisos VPC: OK"
            else
                echo "❌ Permisos VPC: Faltantes"
            fi
            ;;
        "logs")
            if aws logs describe-log-groups --profile sistema-in &> /dev/null; then
                echo "✅ Permisos CloudWatch Logs: OK"
            else
                echo "❌ Permisos CloudWatch Logs: Faltantes"
            fi
            ;;
    esac
done

echo ""
echo "🎉 Configuración de credenciales completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. cd terraform"
echo "2. cp terraform.tfvars.example terraform.tfvars"
echo "3. terraform init"
echo "4. terraform plan"
echo "5. terraform apply"
echo ""
echo "💡 Tip: Si tienes problemas de permisos, contacta a tu administrador AWS"