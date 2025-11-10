# Outputs for Sistema de Detección de Infracciones de Tránsito - Simple Setup

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public.id
}

# EC2 Instance Outputs
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.main.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_eip.main.public_ip
}

output "instance_private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.main.private_ip
}

output "elastic_ip" {
  description = "Elastic IP address"
  value       = aws_eip.main.public_ip
}

# Application URLs
output "application_urls" {
  description = "Application URLs"
  value = {
    frontend      = "http://${aws_eip.main.public_ip}:3002"
    django_api    = "http://${aws_eip.main.public_ip}:8000"
    django_admin  = "http://${aws_eip.main.public_ip}:8000/admin/"
    inference_api = "http://${aws_eip.main.public_ip}:8001"
    rabbitmq_mgmt = "http://${aws_eip.main.public_ip}:15672"
    minio_console = "http://${aws_eip.main.public_ip}:9001"
    grafana       = "http://${aws_eip.main.public_ip}:3001"
    prometheus    = "http://${aws_eip.main.public_ip}:9090"
  }
}

# SSH Connection
output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = var.key_name != "" ? "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_eip.main.public_ip}" : "No key pair specified - use Systems Manager Session Manager instead"
}

# Security Group ID
output "security_group_id" {
  description = "Security group ID for the EC2 instance"
  value       = aws_security_group.ec2.id
}

# Instance Info
output "instance_info" {
  description = "Complete instance information"
  value = {
    instance_type     = aws_instance.main.instance_type
    ami_id            = aws_instance.main.ami
    availability_zone = aws_instance.main.availability_zone
    public_dns        = aws_instance.main.public_dns
  }
}

# Key Pair Outputs
output "key_pair_name" {
  description = "Name of the created key pair"
  value       = aws_key_pair.main.key_name
}

output "ssh_connection_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${aws_key_pair.main.key_name}.pem ec2-user@${aws_eip.main.public_ip}"
}