# Terraform para Infrastructure as Code
# Proveedor AWS
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
  }

  backend "s3" {
    bucket = "traffic-system-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-west-2"
    
    dynamodb_table = "traffic-system-terraform-locks"
    encrypt        = true
  }
}

# Configuración del proveedor AWS
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "traffic-system"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "traffic-system"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_groups" {
  description = "EKS node groups configuration"
  type = map(object({
    desired_size    = number
    max_size        = number
    min_size        = number
    instance_types  = list(string)
    capacity_type   = string
    disk_size       = number
  }))
  default = {
    general = {
      desired_size   = 3
      max_size       = 10
      min_size       = 1
      instance_types = ["t3.large"]
      capacity_type  = "ON_DEMAND"
      disk_size      = 50
    }
    ml_workloads = {
      desired_size   = 2
      max_size       = 5
      min_size       = 0
      instance_types = ["c5.2xlarge"]
      capacity_type  = "SPOT"
      disk_size      = 100
    }
  }
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-${var.environment}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "production"
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Tags for EKS
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# Security Groups
resource "aws_security_group" "additional" {
  name_prefix = "${var.cluster_name}-${var.environment}-additional"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = {
    Name = "${var.cluster_name}-${var.environment}-additional"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "${var.cluster_name}-${var.environment}"
  cluster_version = var.cluster_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    for k, v in var.node_groups : k => {
      name = "${var.cluster_name}-${var.environment}-${k}"

      instance_types = v.instance_types
      capacity_type  = v.capacity_type

      min_size     = v.min_size
      max_size     = v.max_size
      desired_size = v.desired_size

      disk_size = v.disk_size

      vpc_security_group_ids = [aws_security_group.additional.id]

      # Taints para ML workloads
      taints = k == "ml_workloads" ? [
        {
          key    = "workload-type"
          value  = "ml"
          effect = "NO_SCHEDULE"
        }
      ] : []

      labels = {
        Environment = var.environment
        NodeGroup   = k
      }

      tags = {
        Environment = var.environment
        NodeGroup   = k
      }
    }
  }

  # Cluster security group
  cluster_security_group_additional_rules = {
    egress_nodes_ephemeral_ports_tcp = {
      description                = "To node 1025-65535"
      protocol                   = "tcp"
      from_port                  = 1025
      to_port                    = 65535
      type                       = "egress"
      source_node_security_group = true
    }
  }

  # Node security group
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 65535
      type        = "ingress"
      self        = true
    }
    
    egress_all = {
      description      = "Node all egress"
      protocol         = "-1"
      from_port        = 0
      to_port          = 0
      type             = "egress"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  }

  tags = {
    Environment = var.environment
  }
}

# RDS para PostgreSQL
resource "aws_db_subnet_group" "main" {
  name       = "${var.cluster_name}-${var.environment}-db-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "${var.cluster_name}-${var.environment}-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.cluster_name}-${var.environment}-rds"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-${var.environment}-rds"
  }
}

resource "aws_db_instance" "main" {
  identifier = "${var.cluster_name}-${var.environment}-db"

  engine         = "postgres"
  engine_version = "15.3"
  instance_class = var.environment == "production" ? "db.r6g.large" : "db.t3.micro"

  allocated_storage     = var.environment == "production" ? 100 : 20
  max_allocated_storage = var.environment == "production" ? 500 : 100
  storage_encrypted     = true

  db_name  = "trafficdb"
  username = "trafficuser"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = var.environment == "production" ? 7 : 1
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"

  skip_final_snapshot = var.environment != "production"
  deletion_protection = var.environment == "production"

  performance_insights_enabled = var.environment == "production"
  monitoring_interval         = var.environment == "production" ? 60 : 0

  tags = {
    Name = "${var.cluster_name}-${var.environment}-db"
  }
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

# ElastiCache para Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.cluster_name}-${var.environment}-redis-subnet-group"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.cluster_name}-${var.environment}-redis"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-${var.environment}-redis"
  }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.cluster_name}-${var.environment}-redis"
  description                = "Redis cluster for Traffic System"

  node_type            = var.environment == "production" ? "cache.r6g.large" : "cache.t3.micro"
  port                 = 6379
  parameter_group_name = "default.redis7"

  num_cache_clusters = var.environment == "production" ? 2 : 1

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled          = var.environment == "production"

  tags = {
    Name = "${var.cluster_name}-${var.environment}-redis"
  }
}

# S3 para almacenamiento de objetos
resource "aws_s3_bucket" "storage" {
  bucket = "${var.cluster_name}-${var.environment}-storage-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "${var.cluster_name}-${var.environment}-storage"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "storage" {
  bucket = aws_s3_bucket.storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "storage" {
  bucket = aws_s3_bucket.storage.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "storage" {
  bucket = aws_s3_bucket.storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM para acceso a S3
resource "aws_iam_role" "s3_access" {
  name = "${var.cluster_name}-${var.environment}-s3-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = module.eks.oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${replace(module.eks.cluster_oidc_issuer_url, "https://", "")}:sub": "system:serviceaccount:traffic-system:traffic-system-sa"
            "${replace(module.eks.cluster_oidc_issuer_url, "https://", "")}:aud": "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "s3_access" {
  name = "${var.cluster_name}-${var.environment}-s3-access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.storage.arn,
          "${aws_s3_bucket.storage.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.s3_access.name
  policy_arn = aws_iam_policy.s3_access.arn
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "cluster" {
  name              = "/aws/eks/${var.cluster_name}-${var.environment}/cluster"
  retention_in_days = var.environment == "production" ? 30 : 7

  tags = {
    Name = "${var.cluster_name}-${var.environment}-cluster-logs"
  }
}

# Outputs
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "region" {
  description = "AWS region"
  value       = var.aws_region
}

output "cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = module.eks.cluster_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.main.configuration_endpoint_address
}

output "s3_bucket" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.storage.bucket
}

output "s3_access_role_arn" {
  description = "IAM role ARN for S3 access"
  value       = aws_iam_role.s3_access.arn
}