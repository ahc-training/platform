terraform {
  required_providers {
    libvirt = {
      source = "dmacvicar/libvirt"
      version = "0.7.0"
    }
  }
}

variable "hostname" {
    type = string
}

variable "ip" {
    type = string
}

variable "volume-qcow2" {
}

variable "common-init" {
}

variable "k8s_network" {
}

resource "libvirt_volume" "k8s-cp-qcow2" {
  pool = var.volume-qcow2.pool
  base_volume_id = var.volume-qcow2.id
  name = "${var.hostname}-qcow2"
  size = 53687091200
}

resource "libvirt_domain" "k8s-cp" {
  name   = var.hostname
  memory = "12288"
  vcpu   = 4

  autostart = true
  cloudinit = var.common-init.id

  network_interface {
    network_name = var.k8s_network.name
    wait_for_lease = true
    hostname = var.hostname
    addresses = [ var.ip ]
  }

  disk {
    volume_id = libvirt_volume.k8s-cp-qcow2.id
  }

  console {
    type = "pty"
    target_type = "serial"
    target_port = "0"
  }

  graphics {
    type = "spice"
    listen_type = "address"
    autoport = true
  }
}

# output "ip" {
#   value = libvirt_domain.k8s-cp-1.network_interface[0].addresses[0]
# }