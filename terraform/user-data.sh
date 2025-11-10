#!/bin/bash

# Sistema de Detección de Infracciones de Tránsito - EC2 Setup Script

set -e

# Redirect all output to log file and console
exec > >(tee -a /var/log/user-data.log)
exec 2>&1

echo "🚀 Starting Sistema IN setup on EC2..."
echo "📅 Date: $(date)"
echo "💻 Instance: $(curl -s http://169.254.169.254/latest/meta-data/instance-id || echo 'unknown')"

# Update system
echo "📦 Updating system packages..."
yum update -y

# Install Docker (latest version)
echo "🐳 Installing Docker..."
# Remove old docker if exists
yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

# Install Docker CE repository
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install latest Docker CE
yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose standalone (backup method)
echo "🐙 Installing Docker Compose standalone..."
echo "Installing Docker Compose version: ${COMPOSE_VERSION}"

# Download and install specific version
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create symlink
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Wait for Docker to be ready
echo "⏳ Waiting for Docker to be ready..."
sleep 10

# Verify Docker Buildx (should be included with Docker CE)
echo "🔧 Configuring Docker Buildx..."
# Test basic docker functionality first
docker --version
docker-compose --version

# Configure buildx for ec2-user (run after user is properly set up)
echo "🔧 Setting up buildx builder..."
# Configure buildx for ec2-user (run after user is properly set up)
echo "🔧 Setting up buildx builder..."

# Create and use a new builder instance (run as root first, then configure for user)
docker buildx create --name mybuilder --use || echo "Builder already exists"
docker buildx inspect --bootstrap || echo "Buildx bootstrap failed, continuing..."

# Install Git
echo "📁 Installing Git..."
yum install -y git

# Install AWS CLI v2
echo "☁️ Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Install CloudWatch agent
echo "📊 Installing CloudWatch agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm
rm amazon-cloudwatch-agent.rpm

# Install htop for monitoring
echo "🔍 Installing system tools..."
yum install -y htop tree nano

# Create application directory
echo "📂 Setting up application directory..."
mkdir -p /opt/sistema-in
cd /opt/sistema-in

# Create docker-compose.override.yml for production
echo "⚙️ Creating production docker-compose override..."
cat > docker-compose.override.yml << 'EOF'
version: '3.8'

services:
  django:
    ports:
      - "80:8000"  # Map port 80 to Django for main access
      - "8000:8000"  # Keep original port for API access
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=*
    restart: unless-stopped

  inference:
    restart: unless-stopped

  frontend:
    restart: unless-stopped

  postgres:
    restart: unless-stopped

  redis:
    restart: unless-stopped

  rabbitmq:
    restart: unless-stopped

  minio:
    restart: unless-stopped
EOF

# Create deployment script with buildx support
echo "🚀 Creating deployment script..."
cat > deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Please run this script from the sistema_in directory."
    exit 1
fi

# Pull latest code (if git repo exists)
if [ -d ".git" ]; then
    echo "📥 Pulling latest code..."
    git pull origin master || git pull origin main || echo "⚠️ Could not pull from git. Continuing with local code..."
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Ensure buildx is available and configured
echo "🔧 Checking Docker Buildx..."
if ! docker buildx ls | grep -q mybuilder; then
    echo "Creating buildx builder..."
    docker buildx create --name mybuilder --use
    docker buildx inspect --bootstrap
fi

# Build images with buildx
echo "🔨 Building Docker images..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build --no-cache

# Start services
echo "▶️ Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 60

# Check service health
echo "🏥 Checking service health..."
echo "Django API:" 
curl -f http://localhost:8000/api/health/ || echo "⚠️ Django not ready yet"

echo "Inference Service:"
curl -f http://localhost:8001/api/v1/health || echo "⚠️ Inference service not ready yet"

echo "Frontend:"
curl -f http://localhost:3002 || echo "⚠️ Frontend not ready yet"

echo "✅ Deployment completed!"
echo ""
echo "🌐 Access your application at:"
echo "  Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3002"
echo "  Django API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "  Django Admin: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/admin/"
echo "  Inference API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8001"
echo "  RabbitMQ Management: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):15672"
echo "  MinIO Console: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9001"
echo "  Grafana: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3001"
echo "  Prometheus: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):9090"
EOF

chmod +x deploy.sh

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > monitor.sh << 'EOF'
#!/bin/bash

echo "🖥️ Sistema IN - System Status"
echo "==============================="
echo ""

echo "📊 System Resources:"
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "  CPU: " 100 - $1 "%"}'

echo "Memory Usage:"
free -h | awk 'NR==2{printf "  RAM: %s/%s (%.2f%%)\n", $3,$2,$3*100/$2 }'

echo "Disk Usage:"
df -h / | awk 'NR==2{printf "  Disk: %s/%s (%s)\n", $3,$2,$5}'

echo ""
echo "🐳 Docker Services:"
docker-compose ps

echo ""
echo "📋 Docker Container Stats:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo "📝 Recent Logs (last 10 lines):"
echo "Django:"
docker-compose logs --tail=5 django 2>/dev/null | tail -5

echo ""
echo "Inference:"
docker-compose logs --tail=5 inference 2>/dev/null | tail -5
EOF

chmod +x monitor.sh

# Create restart script
echo "🔄 Creating restart script..."
cat > restart.sh << 'EOF'
#!/bin/bash
echo "🔄 Restarting Sistema IN services..."
docker-compose restart
echo "✅ All services restarted"
EOF

chmod +x restart.sh

# Create logs script
echo "📝 Creating logs script..."
cat > logs.sh << 'EOF'
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <service_name>"
    echo "Available services:"
    docker-compose ps --services
    exit 1
fi

echo "📝 Showing logs for service: $1"
docker-compose logs -f "$1"
EOF

chmod +x logs.sh

# Create system service for auto-start
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/sistema-in.service << EOF
[Unit]
Description=Sistema de Detección de Infracciones de Tránsito
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/sistema-in
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=300
User=ec2-user
Group=ec2-user

[Install]
WantedBy=multi-user.target
EOF

# Enable the service (but don't start it yet - will start after code is deployed)
systemctl daemon-reload
systemctl enable sistema-in.service

# Create CloudWatch agent configuration
echo "📊 Setting up CloudWatch monitoring..."
mkdir -p /opt/aws/amazon-cloudwatch-agent/etc
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/messages",
                        "log_group_name": "/aws/ec2/${project_name}/system",
                        "log_stream_name": "{instance_id}/messages"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "Sistema-IN/EC2",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_iowait", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": ["used_percent"],
                "metrics_collection_interval": 60,
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": 60
            },
            "swap": {
                "measurement": ["swap_used_percent"],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

# Set proper permissions
chown -R ec2-user:ec2-user /opt/sistema-in

# Create welcome message
cat > /etc/motd << 'EOF'
 ____  _     _                        ___ _   _ 
/ ___|(_)___| |_ ___ _ __ ___   __ _   |_ _| \ | |
\___ \| / __| __/ _ \ '_ ` _ \ / _` |   | ||  \| |
 ___) | \__ \ ||  __/ | | | | | (_| |   | || |\  |
|____/|_|___/\__\___|_| |_| |_|\__,_|  |___|_| \_|

Sistema de Detección de Infracciones de Tránsito

📂 Application directory: /opt/sistema-in
🚀 Deploy: cd /opt/sistema-in && ./deploy.sh  
📊 Monitor: cd /opt/sistema-in && ./monitor.sh
🔄 Restart: cd /opt/sistema-in && ./restart.sh
📝 Logs: cd /opt/sistema-in && ./logs.sh <service>

🌐 Access URLs (replace <IP> with your instance IP):
  Frontend: http://<IP>:3002
  Django API: http://<IP>:8000
  Django Admin: http://<IP>:8000/admin/
  Inference API: http://<IP>:8001

For more info: cat /opt/sistema-in/README-DEPLOYMENT.md
EOF

# Create README for deployment
cat > /opt/sistema-in/README-DEPLOYMENT.md << 'EOF'
# Sistema IN - Deployment Guide

## Quick Start

1. Clone your repository:
   ```bash
   cd /opt/sistema-in
   git clone https://github.com/your-username/sistema_in.git .
   ```

2. Deploy the application:
   ```bash
   ./deploy.sh
   ```

## Management Scripts

- `./deploy.sh` - Deploy/redeploy the application
- `./monitor.sh` - Check system and container status  
- `./restart.sh` - Restart all services
- `./logs.sh <service>` - View logs for a specific service

## Service Management

View all services:
```bash
docker-compose ps
```

Restart specific service:
```bash
docker-compose restart <service_name>
```

View logs:
```bash
docker-compose logs -f <service_name>
```

## System Service

The application is configured as a systemd service:
```bash
sudo systemctl status sistema-in
sudo systemctl start sistema-in
sudo systemctl stop sistema-in
```

## Monitoring

- System metrics are sent to CloudWatch
- Application logs are available via `docker-compose logs`
- Access Grafana at http://<IP>:3001 for dashboards
- Access Prometheus at http://<IP>:9090 for metrics

## Troubleshooting

1. Check system resources: `./monitor.sh`
2. Check service status: `docker-compose ps`
3. Check logs: `./logs.sh <service_name>`
4. Restart services: `./restart.sh`
EOF

chown ec2-user:ec2-user /opt/sistema-in/README-DEPLOYMENT.md

# Final verification and status report
echo ""
echo "🔍 Performing final system verification..."

# Verify installations
echo "📋 Checking installed software versions:"
echo "  ✅ Git: $(git --version 2>/dev/null || echo '❌ Not installed')"
echo "  ✅ Docker: $(docker --version 2>/dev/null || echo '❌ Not installed')"
echo "  ✅ Docker Compose: $(docker-compose --version 2>/dev/null || echo '❌ Not installed')"
echo "  ✅ AWS CLI: $(aws --version 2>/dev/null | head -1 || echo '❌ Not installed')"

# Check Docker service
echo "🐳 Docker service status:"
systemctl is-active docker && echo "  ✅ Docker is running" || echo "  ❌ Docker is not running"

# Check if ec2-user can use docker
echo "👤 User permissions:"
groups ec2-user | grep -q docker && echo "  ✅ ec2-user is in docker group" || echo "  ❌ ec2-user not in docker group"

# Test Docker functionality
echo "🧪 Testing Docker functionality:"
if docker run --rm hello-world > /dev/null 2>&1; then
    echo "  ✅ Docker can run containers"
else
    echo "  ❌ Docker container test failed"
fi

# Check Docker Buildx
echo "🔧 Docker Buildx status:"
if docker buildx ls | grep -q mybuilder; then
    echo "  ✅ Buildx builder 'mybuilder' exists"
else
    echo "  ❌ Buildx builder not configured"
fi

echo ""
echo "✅ EC2 setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. SSH into your instance: ssh -i sistema-in-key.pem ec2-user@\$(terraform output -raw instance_public_ip)"
echo "2. cd /opt/sistema-in"  
echo "3. Clone your repository: git clone https://github.com/dbacilio88/sistema_in.git ."
echo "4. Run: ./deploy.sh"
echo ""
echo "🌐 Your instance will be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'IP-NOT-AVAILABLE')"
echo ""
echo "📊 Setup completed at: $(date)"