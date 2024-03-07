terraform {
  required_providers {
    libvirt = {
      source = "dmacvicar/libvirt"
      version = "0.7.6"
    }
    ansible = {
        version = "~> 1.1.0"
        source  = "ansible/ansible"
    }
    helm = {
      source = "hashicorp/helm"
      version = "2.12.1"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "2.24.0"
    }
  }
}

provider "libvirt" {
  uri = local.libvirt.uri
}

provider "ansible" {

}

provider "helm" {
    kubernetes {
        config_path = local.kubernetes.config
    }
}

provider "kubernetes" {
    config_path = local.kubernetes.config
}