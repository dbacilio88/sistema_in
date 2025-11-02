# Configuración para múltiples entornos
environments = {
  development = {
    aws_region      = "us-west-2"
    cluster_name    = "traffic-system-dev"
    cluster_version = "1.28"
    
    node_groups = {
      general = {
        desired_size   = 1
        max_size       = 3
        min_size       = 1
        instance_types = ["t3.medium"]
        capacity_type  = "SPOT"
        disk_size      = 20
      }
    }
    
    # Base de datos más pequeña para desarrollo
    rds_instance_class = "db.t3.micro"
    rds_allocated_storage = 20
    
    # Redis más pequeño
    redis_node_type = "cache.t3.micro"
    redis_num_cache_clusters = 1
  }
  
  staging = {
    aws_region      = "us-west-2"
    cluster_name    = "traffic-system-staging"
    cluster_version = "1.28"
    
    node_groups = {
      general = {
        desired_size   = 2
        max_size       = 5
        min_size       = 1
        instance_types = ["t3.large"]
        capacity_type  = "ON_DEMAND"
        disk_size      = 30
      }
      ml_workloads = {
        desired_size   = 1
        max_size       = 3
        min_size       = 0
        instance_types = ["c5.xlarge"]
        capacity_type  = "SPOT"
        disk_size      = 50
      }
    }
    
    rds_instance_class = "db.t3.small"
    rds_allocated_storage = 50
    
    redis_node_type = "cache.t3.small"
    redis_num_cache_clusters = 1
  }
  
  production = {
    aws_region      = "us-west-2"
    cluster_name    = "traffic-system-prod"
    cluster_version = "1.28"
    
    node_groups = {
      general = {
        desired_size   = 3
        max_size       = 10
        min_size       = 2
        instance_types = ["t3.large"]
        capacity_type  = "ON_DEMAND"
        disk_size      = 50
      }
      ml_workloads = {
        desired_size   = 2
        max_size       = 8
        min_size       = 1
        instance_types = ["c5.2xlarge", "c5.4xlarge"]
        capacity_type  = "SPOT"
        disk_size      = 100
      }
      database = {
        desired_size   = 2
        max_size       = 4
        min_size       = 2
        instance_types = ["r5.large"]
        capacity_type  = "ON_DEMAND"
        disk_size      = 100
      }
    }
    
    rds_instance_class = "db.r6g.large"
    rds_allocated_storage = 200
    rds_max_allocated_storage = 1000
    
    redis_node_type = "cache.r6g.large"
    redis_num_cache_clusters = 3
  }
}

# Variables comunes
common_tags = {
  Project    = "traffic-system"
  ManagedBy  = "terraform"
  Owner      = "platform-team"
  Repository = "sistema_in"
}