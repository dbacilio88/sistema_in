#!/bin/bash
set -e

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1

echo "Starting user-data script at $(date)"

# Update system
echo "Updating system..."
yum update -y

# Install Git
echo "Installing Git..."
yum install -y git

# Install Docker using amazon-linux-extras (correct method for Amazon Linux 2)
echo "Installing Docker via amazon-linux-extras..."
amazon-linux-extras install docker -y

# Start Docker service
echo "Starting Docker service..."
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group
echo "Adding ec2-user to docker group..."
usermod -a -G docker ec2-user

# Install Docker Compose
echo "Installing Docker Compose..."
COMPOSE_VERSION="${COMPOSE_VERSION}"
curl -L "https://github.com/docker/compose/releases/download/$COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verify installations
echo "Verifying installations..."
git --version
docker --version
docker-compose --version

# Create app directory
echo "Creating application directory..."
mkdir -p /opt/sistema-in
chown ec2-user:ec2-user /opt/sistema-in

# Create simple deploy script
echo "Creating deploy script..."
cat > /opt/sistema-in/deploy.sh << 'EOF'
#!/bin/bash
set -e
echo "Starting deployment..."
cd /opt/sistema-in
if [ -d ".git" ]; then
    echo "Pulling latest changes..."
    git pull || echo "Could not pull from git"
fi
echo "Stopping existing containers..."
docker-compose down || true
echo "Building and starting containers..."
docker-compose up -d --build
echo "Deployment completed!"
echo "Container status:"
docker-compose ps
EOF

# Create AWS deployment script
cat > /opt/sistema-in/deploy-aws.sh << 'EOF'
#!/bin/bash
set -e
echo "🚀 Desplegando Sistema IN en AWS..."

# Obtener IP pública
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
echo "🌐 IP Pública: $PUBLIC_IP"

export PUBLIC_IP=$PUBLIC_IP
cd /opt/sistema-in

if [ -d ".git" ]; then
    echo "📥 Actualizando código..."
    git pull || echo "⚠️ No se pudo actualizar"
fi

echo "⏹️ Deteniendo servicios..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml down || true

echo "🔨 Construyendo..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml build

echo "🚀 Iniciando servicios..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml up -d

echo "✅ Deployment completado!"
echo "🌐 Frontend: http://$PUBLIC_IP:3002"
echo "🔧 Backend:  http://$PUBLIC_IP:8000"
EOF

chmod +x /opt/sistema-in/deploy.sh
chmod +x /opt/sistema-in/deploy-aws.sh
chown ec2-user:ec2-user /opt/sistema-in/deploy.sh
chown ec2-user:ec2-user /opt/sistema-in/deploy-aws.sh

echo "User-data script completed successfully at $(date)"