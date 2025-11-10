# Sistema IN - AWS Infrastructure

This directory contains Terraform configuration for deploying the Sistema de Detección de Infracciones de Tránsito to AWS using a simple single EC2 instance approach.

## Architecture

- **Single EC2 Instance**: t3.xlarge (4 vCPUs, 16 GB RAM) running all services via Docker Compose
- **VPC**: Simple VPC with one public subnet
- **Security Group**: Configured to allow all necessary ports
- **Storage**: 50 GB encrypted EBS volume
- **Monitoring**: CloudWatch agent for basic monitoring

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **Terraform installed** (version >= 1.5)
3. **AWS Key Pair** (optional, for SSH access)

## Quick Deployment

1. **Configure variables**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your preferences
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Plan deployment**:
   ```bash
   terraform plan
   ```

4. **Deploy infrastructure**:
   ```bash
   terraform apply
   ```

5. **Get connection info**:
   ```bash
   terraform output
   ```

## After Deployment

Once the infrastructure is deployed, connect to your instance and deploy the application:

### Option 1: SSH Access (if you configured a key pair)
```bash
# Get the SSH command from Terraform output
terraform output ssh_command

# SSH into the instance
ssh -i ~/.ssh/your-key.pem ec2-user@<instance-ip>
```

### Option 2: AWS Systems Manager Session Manager
```bash
# Get the instance ID
INSTANCE_ID=$(terraform output -raw instance_id)

# Connect via Session Manager
aws ssm start-session --target $INSTANCE_ID
```

### Deploy the Application

Once connected to the instance:

```bash
# Navigate to application directory
cd /opt/sistema-in

# Clone your repository
git clone https://github.com/your-username/sistema_in.git .

# Deploy the application
./deploy.sh
```

## Application URLs

After deployment, your application will be available at:

- **Frontend**: http://`<instance-ip>`:3002
- **Django API**: http://`<instance-ip>`:8000
- **Django Admin**: http://`<instance-ip>`:8000/admin/
- **Inference API**: http://`<instance-ip>`:8001
- **RabbitMQ Management**: http://`<instance-ip>`:15672
- **MinIO Console**: http://`<instance-ip>`:9001
- **Grafana**: http://`<instance-ip>`:3001
- **Prometheus**: http://`<instance-ip>`:9090

## Management Scripts

The EC2 instance includes several management scripts in `/opt/sistema-in/`:

- `./deploy.sh` - Deploy/redeploy the application
- `./monitor.sh` - Check system and container status
- `./restart.sh` - Restart all services
- `./logs.sh <service>` - View logs for a specific service

## Monitoring

- System metrics are automatically sent to CloudWatch
- Use `./monitor.sh` to check system status
- Access Grafana dashboards for application monitoring
- View container logs with `./logs.sh <service_name>`

## Security Considerations

⚠️ **Important**: This configuration opens several ports to the internet (0.0.0.0/0) for demonstration purposes. For production:

1. Restrict access to specific IP ranges
2. Use a load balancer with SSL termination
3. Consider using AWS secrets manager for sensitive data
4. Implement proper backup strategies

## Cost Optimization

The t3.xlarge instance costs approximately:
- **On-Demand**: ~$150/month
- **Reserved Instance (1 year)**: ~$95/month
- **Spot Instance**: ~$45-75/month (variable)

Consider using Spot Instances for development environments.

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

## Troubleshooting

### Instance not accessible
1. Check security group rules
2. Verify the instance is in a public subnet
3. Ensure the internet gateway is properly configured

### Application not starting
1. SSH/connect to the instance
2. Check Docker service: `sudo systemctl status docker`
3. Check application logs: `cd /opt/sistema-in && ./logs.sh <service>`
4. Monitor system resources: `./monitor.sh`

### Port access issues
1. Verify security group allows the required ports
2. Check if services are running: `docker-compose ps`
3. Verify port mapping in docker-compose files

## Support

For issues with the Terraform configuration, check:
1. AWS credentials and permissions
2. Terraform version compatibility
3. AWS service limits in your region