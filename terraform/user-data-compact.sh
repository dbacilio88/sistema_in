#!/bin/bash
set -e
exec > >(tee -a /var/log/user-data.log) 2>&1

echo "🚀 Starting Sistema IN setup..."
yum update -y

echo "🐳 Installing Docker CE..."
yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

echo "🐙 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

echo "📁 Installing Git..."
yum install -y git

echo "☁️ Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

echo "🔍 Installing tools..."
yum install -y htop tree nano

echo "📂 Setting up application..."
mkdir -p /opt/sistema-in
cd /opt/sistema-in

cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  backend:
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://sistema_user:sistema_pass@db:5432/sistema_db
  frontend:
    environment:
      - NODE_ENV=production
EOF

cat > deploy.sh << 'EOF'
#!/bin/bash
set -e
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi
if [ -d ".git" ]; then
    git pull origin master || git pull origin main || echo "⚠️ Could not pull"
fi
docker-compose down
if ! docker buildx ls | grep -q mybuilder; then
    docker buildx create --name mybuilder --use
    docker buildx inspect --bootstrap
fi
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build --no-cache
docker-compose up -d
echo "✅ Deployment completed"
docker-compose ps
EOF

chmod +x deploy.sh
chown -R ec2-user:ec2-user /opt/sistema-in

echo "✅ Setup completed!"
echo "Next: ssh -i sistema-in-key.pem ec2-user@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"