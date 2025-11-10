# Variables for Sistema de Detección de Infracciones de Tránsito - Simple Setup

# General Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "sistema-in"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# EC2 Configuration
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.xlarge" # 4 vCPUs, 16 GB RAM for running all services
}

variable "volume_size" {
  description = "Size of the EBS volume in GB"
  type        = number
  default     = 50
}

variable "key_name" {
  description = "AWS Key Pair name for EC2 instance (optional)"
  type        = string
  default     = ""
}

variable "public_key" {
  description = "Public key content for SSH access to EC2 instance (optional, will use default if not provided)"
  type        = string
  default     = ""
}

# AWS Credentials (for CI/CD or when not using AWS profiles)
variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type        = string
  default     = ""
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type        = string
  default     = ""
  sensitive   = true
}