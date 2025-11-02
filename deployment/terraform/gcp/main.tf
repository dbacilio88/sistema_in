# Configuración para Google Cloud Platform
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
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

  backend "gcs" {
    bucket = "traffic-system-terraform-state"
    prefix = "terraform/state"
  }
}

# Configuración del proveedor Google Cloud
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Variables
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
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
  description = "GKE cluster name"
  type        = string
  default     = "traffic-system"
}

# Enable APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "compute.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_dependent_services = true
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "${var.cluster_name}-${var.environment}-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id

  depends_on = [google_project_service.apis]
}

# Subnet para GKE
resource "google_compute_subnetwork" "gke" {
  name          = "${var.cluster_name}-${var.environment}-gke-subnet"
  ip_cidr_range = "10.1.0.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  project       = var.project_id

  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = "10.2.0.0/16"
  }

  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = "10.3.0.0/20"
  }

  private_ip_google_access = true
}

# Subnet para bases de datos
resource "google_compute_subnetwork" "database" {
  name          = "${var.cluster_name}-${var.environment}-db-subnet"
  ip_cidr_range = "10.4.0.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  project       = var.project_id

  private_ip_google_access = true
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.cluster_name}-${var.environment}-allow-internal"
  network = google_compute_network.main.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.1.0.0/24", "10.2.0.0/16", "10.3.0.0/20", "10.4.0.0/24"]
}

# Service Account para GKE
resource "google_service_account" "gke_nodes" {
  account_id   = "${var.cluster_name}-${var.environment}-gke-nodes"
  display_name = "GKE Nodes Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "gke_nodes" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

# GKE Cluster
resource "google_container_cluster" "main" {
  name     = "${var.cluster_name}-${var.environment}"
  location = var.region
  project  = var.project_id

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.main.id
  subnetwork = google_compute_subnetwork.gke.id

  # Networking configuration
  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods"
    services_secondary_range_name = "gke-services"
  }

  # Security configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "10.5.0.0/28"
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All networks"
    }
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Network policy
  network_policy {
    enabled = true
  }

  addons_config {
    http_load_balancing {
      disabled = false
    }

    horizontal_pod_autoscaling {
      disabled = false
    }

    network_policy_config {
      disabled = false
    }
  }

  # Maintenance policy
  maintenance_policy {
    recurring_window {
      start_time = "2023-01-01T00:00:00Z"
      end_time   = "2023-01-01T04:00:00Z"
      recurrence = "FREQ=WEEKLY;BYDAY=SA"
    }
  }

  # Logging and monitoring
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"

  depends_on = [
    google_project_service.apis,
    google_compute_subnetwork.gke
  ]
}

# Node Pool General
resource "google_container_node_pool" "general" {
  name       = "general"
  location   = var.region
  cluster    = google_container_cluster.main.name
  project    = var.project_id

  node_count = var.environment == "production" ? 3 : 2

  autoscaling {
    min_node_count = var.environment == "production" ? 2 : 1
    max_node_count = var.environment == "production" ? 10 : 5
  }

  node_config {
    preemptible  = var.environment != "production"
    machine_type = var.environment == "production" ? "e2-standard-4" : "e2-standard-2"

    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment = var.environment
      node-pool   = "general"
    }

    disk_size_gb = var.environment == "production" ? 50 : 30
    disk_type    = "pd-ssd"

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# Node Pool para ML Workloads
resource "google_container_node_pool" "ml_workloads" {
  name       = "ml-workloads"
  location   = var.region
  cluster    = google_container_cluster.main.name
  project    = var.project_id

  node_count = var.environment == "production" ? 2 : 1

  autoscaling {
    min_node_count = 0
    max_node_count = var.environment == "production" ? 8 : 3
  }

  node_config {
    preemptible  = true  # Always use preemptible for ML workloads
    machine_type = var.environment == "production" ? "c2-standard-8" : "c2-standard-4"

    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment   = var.environment
      node-pool     = "ml-workloads"
      workload-type = "ml"
    }

    taint {
      key    = "workload-type"
      value  = "ml"
      effect = "NO_SCHEDULE"
    }

    disk_size_gb = 100
    disk_type    = "pd-ssd"

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "main" {
  name             = "${var.cluster_name}-${var.environment}-postgres"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id

  settings {
    tier = var.environment == "production" ? "db-standard-2" : "db-f1-micro"

    disk_type    = "PD_SSD"
    disk_size    = var.environment == "production" ? 100 : 20
    disk_autoresize = true
    disk_autoresize_limit = var.environment == "production" ? 500 : 100

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = var.environment == "production"
      backup_retention_settings {
        retained_backups = var.environment == "production" ? 30 : 7
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
      require_ssl     = true
    }

    database_flags {
      name  = "log_statement"
      value = "all"
    }

    insights_config {
      query_insights_enabled  = true
      record_application_tags = true
      record_client_address   = true
    }
  }

  depends_on = [
    google_project_service.apis,
    google_compute_global_address.private_ip_address,
    google_service_networking_connection.private_vpc_connection
  ]

  deletion_protection = var.environment == "production"
}

resource "google_sql_database" "main" {
  name     = "trafficdb"
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

resource "google_sql_user" "main" {
  name     = "trafficuser"
  instance = google_sql_database_instance.main.name
  password = random_password.postgres_password.result
  project  = var.project_id
}

resource "random_password" "postgres_password" {
  length  = 16
  special = true
}

# Private IP para Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.cluster_name}-${var.environment}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
  project       = var.project_id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Memorystore Redis
resource "google_redis_instance" "main" {
  name           = "${var.cluster_name}-${var.environment}-redis"
  tier           = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = var.environment == "production" ? 4 : 1
  region         = var.region
  project        = var.project_id

  location_id             = var.zone
  alternative_location_id = var.environment == "production" ? "${substr(var.region, 0, length(var.region)-1)}b" : null

  authorized_network = google_compute_network.main.id

  redis_version     = "REDIS_7_0"
  display_name      = "Traffic System Redis"
  auth_enabled      = true
  transit_encryption_mode = "SERVER_CLIENT"

  depends_on = [google_project_service.apis]
}

# Cloud Storage
resource "google_storage_bucket" "main" {
  name     = "${var.cluster_name}-${var.environment}-storage-${random_id.bucket_suffix.hex}"
  location = var.region
  project  = var.project_id

  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = var.environment == "production" ? 90 : 30
    }
    action {
      type = "Delete"
    }
  }

  uniform_bucket_level_access = true

  depends_on = [google_project_service.apis]
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Service Account para aplicaciones
resource "google_service_account" "app" {
  account_id   = "${var.cluster_name}-${var.environment}-app"
  display_name = "Traffic System Application Service Account"
  project      = var.project_id
}

# IAM bindings para Storage
resource "google_storage_bucket_iam_member" "app_storage" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app.email}"
}

# IAM binding para Cloud SQL
resource "google_project_iam_member" "app_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# Secret Manager
resource "google_secret_manager_secret" "postgres_password" {
  secret_id = "${var.cluster_name}-${var.environment}-postgres-password"
  project   = var.project_id

  replication {
    automatic = true
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "postgres_password" {
  secret      = google_secret_manager_secret.postgres_password.id
  secret_data = random_password.postgres_password.result
}

resource "google_secret_manager_secret" "redis_auth" {
  secret_id = "${var.cluster_name}-${var.environment}-redis-auth"
  project   = var.project_id

  replication {
    automatic = true
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "redis_auth" {
  secret      = google_secret_manager_secret.redis_auth.id
  secret_data = google_redis_instance.main.auth_string
}

# IAM para acceso a secrets
resource "google_secret_manager_secret_iam_member" "postgres_password" {
  secret_id = google_secret_manager_secret.postgres_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app.email}"
}

resource "google_secret_manager_secret_iam_member" "redis_auth" {
  secret_id = google_secret_manager_secret.redis_auth.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app.email}"
}

# Workload Identity binding
resource "google_service_account_iam_member" "workload_identity" {
  service_account_id = google_service_account.app.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[traffic-system/traffic-system-sa]"
}

# Cloud Monitoring
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notifications"
  type         = "email"
  project      = var.project_id

  labels = {
    email_address = "admin@example.com"  # Cambiar por email real
  }

  depends_on = [google_project_service.apis]
}

# Outputs
output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.main.name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.main.endpoint
}

output "cluster_location" {
  description = "GKE cluster location"
  value       = google_container_cluster.main.location
}

output "postgres_connection_name" {
  description = "PostgreSQL connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "postgres_private_ip" {
  description = "PostgreSQL private IP"
  value       = google_sql_database_instance.main.private_ip_address
}

output "redis_host" {
  description = "Redis host"
  value       = google_redis_instance.main.host
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.main.port
}

output "storage_bucket" {
  description = "Storage bucket name"
  value       = google_storage_bucket.main.name
}

output "service_account_email" {
  description = "Application service account email"
  value       = google_service_account.app.email
}