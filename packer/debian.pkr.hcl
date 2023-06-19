
variable "iso_url" {
  type = string
}

variable "iso_checksum" {
  type = string
}

variable "ssh_password" {
  type = string
  sensitive = true
}

source "vmware-iso" "debian" {
  iso_url      = var.iso_url
  iso_checksum = "sha512:${var.iso_checksum}"
  ssh_username = "debian"
  ssh_password = var.ssh_password
  ssh_port     = 22
  ssh_wait_timeout = "10000s"
  shutdown_command = "echo var.ssh_password | sudo -S shutdown -P now"
  vm_name     = "packer-debian"
  cpus        = 1
  memory      = 1024
  disk_size   = 8192
  format      = "ovf"
  http_directory = "http"
  cd_files = ["./http/*"]
  cd_label = "seeddata"
  boot_wait = "10s"
  boot_key_interval = "10ms"
  boot_command = [
    "<esc><wait>",
    "install <wait>",
    "auto=true priority=critical file=/mnt/cdrom2/preseed.cfg <wait>",
    "<wait><enter><wait3>",
    "<leftAltOn><f2><leftAltOff>",
    "<wait><enter><wait>",
    "mkdir /mnt/cdrom2<enter><wait>",
    "mount /dev/sr1 /mnt/cdrom2<enter><wait>",
    "mkdir ~/preseed<enter><wait>",
    "cp /mnt/cdrom2/* ~/preseed/<enter><wait>",
    "<leftAltOn><f1><leftAltOff><wait>",    "<enter><wait>"
  ]
  headless = true
  vmx_data = {
    "usb.present" = "TRUE"
    "usb.vbluetooth.startConnected" = "TRUE"
    "ehci.present" = "TRUE"
  }
}

build {
  sources = ["source.vmware-iso.debian"]
}
