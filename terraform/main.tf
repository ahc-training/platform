terraform {
  required_providers {
    libvirt = {
      source = "dmacvicar/libvirt"
      version = "0.7.0"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

variable "ubuntu_version" {
  description = "Ubuntu version"
  default = "20.04"
}

variable "storage_pool" {
  default = "k8s-cluster"
}

variable "iscsi_nodes" {
  default = {
      iscsi-n-1 = "192.167.56.15"
    }
}

variable "k8s_controlplanes" {
  default = {
      k8s-cp-1 = "192.167.56.11"
    }
}

variable "k8s_nodes" {
  default = {
    k8s-n-1 = "192.167.56.12"
    k8s-n-2 = "192.167.56.13"
    }
}

locals {
  ubuntu_img_url = "https://cloud-images.ubuntu.com/releases/${var.ubuntu_version}/release/ubuntu-${var.ubuntu_version}-server-cloudimg-amd64.img"
}

data "template_file" "user_data" {
  template = file("${path.module}/cloud_init.cfg")
}

## Still experimental, does not work with `terraform destroy`
# resource "libvirt_pool" "k8s_cluster" {
#   name = var.storage_pool
#   type = "dir"
#   path = "/data"
# }

resource "libvirt_cloudinit_disk" "common-init" {
  name = "common-init.iso"
  #pool = libvirt_pool.k8s_cluster.name
  pool = var.storage_pool
  user_data = data.template_file.user_data.rendered
}

resource "libvirt_network" "k8s_network" {
  name = "k8snet"
  mode = "nat"
  domain = "k8s.local"
  addresses = [ "192.167.56.0/24" ]
  autostart = true
  dns {
    enabled = true
    local_only = true
  }
  dhcp {
    enabled = true
  }
}

resource "libvirt_volume" "ubuntu-qcow2" {
  name = "ubuntu-qcow2"
  #pool = libvirt_pool.k8s_cluster.name 
  pool = var.storage_pool
  source = local.ubuntu_img_url
  format = "qcow2"
}

module "iscsi" {
  for_each = jsondecode(replace(var.iscsi_nodes, "'", "\""))

  source = "./modules/iscsi"

  hostname = each.key
  ip = each.value
  volume-qcow2 = libvirt_volume.ubuntu-qcow2
  common-init = libvirt_cloudinit_disk.common-init
  k8s_network = libvirt_network.k8s_network
}

module "k8s-controlplane" {
  for_each = jsondecode(replace(var.k8s_controlplanes, "'", "\""))

  source = "./modules/k8s-controlplane"

  hostname = each.key
  ip = each.value
  volume-qcow2 = libvirt_volume.ubuntu-qcow2
  common-init = libvirt_cloudinit_disk.common-init
  k8s_network = libvirt_network.k8s_network
}

module "k8s-node" {
  for_each = jsondecode(replace(var.k8s_nodes, "'", "\""))

  source = "./modules/k8s-node"

  hostname = each.key
  ip = each.value
  volume-qcow2 = libvirt_volume.ubuntu-qcow2
  common-init = libvirt_cloudinit_disk.common-init
  k8s_network = libvirt_network.k8s_network
}