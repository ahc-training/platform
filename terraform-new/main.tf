## Still experimental, does not work with `terraform destroy`
# resource "libvirt_pool" "k8s_cluster" {
#   name = local.libvirt.storage_pool
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
  name = local.libvirt.network.name
  mode = local.libvirt.network.mode
  domain = local.libvirt.network.domain
  addresses = local.libvirt.network.addresses
  autostart = local.libvirt.network.autostart
  dns {
    enabled = local.libvirt.network.dns.enabled
    local_only = local.libvirt.network.dns.local_only
  }
  dhcp {
    enabled = local.libvirt.network.dhcp.enabled
  }
}

resource "libvirt_volume" "ubuntu-qcow2" {
  name = local.libvirt.volume.name
  #pool = libvirt_pool.k8s_cluster.name 
  pool = local.libvirt.volume.storage_pool
  source = local.libvirt.image_url
  format = "qcow2"
}

module "iscsi" {
  for_each = jsondecode(replace(local.iscsi.nodes, "'", "\""))

  source = "./modules/iscsi"

  hostname = each.key
  ip = each.value
  volume-qcow2 = libvirt_volume.ubuntu-qcow2
  common-init = libvirt_cloudinit_disk.common-init
  k8s_network = libvirt_network.k8s_network
}

module "k8s-controlplane" {
  for_each = jsondecode(replace(local.kubernetes.controlplanes, "'", "\""))

  source = "./modules/k8s-controlplane"

  hostname = each.key
  ip = each.value
  volume-qcow2 = libvirt_volume.ubuntu-qcow2
  common-init = libvirt_cloudinit_disk.common-init
  k8s_network = libvirt_network.k8s_network
}

module "k8s-node" {
  for_each = jsondecode(replace(local.kubernetes.nodes, "'", "\""))

  source = "./modules/k8s-node"

  hostname = each.key
  ip = each.value
  volume-qcow2 = libvirt_volume.ubuntu-qcow2
  common-init = libvirt_cloudinit_disk.common-init
  k8s_network = libvirt_network.k8s_network
}