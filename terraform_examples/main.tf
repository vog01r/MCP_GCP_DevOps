# Configuration Terraform pour GCP
# Exemple de déploiement d'une VM avec réseau

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Configuration du provider GCP
provider "google" {
  credentials = file("/opt/git/service-account-key.json")
  project     = "level-surfer-473817-p5"
  region      = "us-central1"
  zone        = "us-central1-a"
}

# Variables
variable "instance_name" {
  description = "Nom de l'instance VM"
  type        = string
  default     = "terraform-vm"
}

variable "machine_type" {
  description = "Type de machine"
  type        = string
  default     = "e2-medium"
}

variable "disk_size_gb" {
  description = "Taille du disque en GB"
  type        = number
  default     = 20
}

# Ressource : Instance VM
resource "google_compute_instance" "vm_instance" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = "us-central1-a"

  tags = ["web-server", "terraform-managed"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = var.disk_size_gb
    }
  }

  network_interface {
    network = "default"

    access_config {
      // IP externe éphémère
    }
  }

  metadata = {
    startup-script = <<-EOF
      #!/bin/bash
      apt-get update
      apt-get install -y nginx
      echo "Hello from Terraform VM!" > /var/www/html/index.html
      systemctl start nginx
      systemctl enable nginx
    EOF
  }

  metadata_startup_script = "echo 'VM créée avec Terraform' > /tmp/terraform-info.txt"
}

# Règle de pare-feu pour HTTP
resource "google_compute_firewall" "http" {
  name    = "allow-http-terraform"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

# Règle de pare-feu pour HTTPS
resource "google_compute_firewall" "https" {
  name    = "allow-https-terraform"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

# Outputs
output "instance_name" {
  description = "Nom de l'instance créée"
  value       = google_compute_instance.vm_instance.name
}

output "instance_external_ip" {
  description = "Adresse IP externe de l'instance"
  value       = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}

output "instance_internal_ip" {
  description = "Adresse IP interne de l'instance"
  value       = google_compute_instance.vm_instance.network_interface[0].network_ip
}

output "instance_id" {
  description = "ID de l'instance"
  value       = google_compute_instance.vm_instance.instance_id
}
