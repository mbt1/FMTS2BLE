
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
  ssh_username = "packer"
  ssh_password = var.ssh_password
  ssh_port     = 22
  ssh_wait_timeout = "10000s"
  shutdown_command = "echo 'packer' | sudo -S shutdown -P now"
  vm_name     = "packer-debian"
  cpus        = 1
  memory      = 1024
  disk_size   = 4096
  format      = "ovf"
  http_directory = "http"
  cd_files = ["./http/*"]
  cd_label = "seeddata"
  boot_wait = "10s"
  boot_command = [
    "<esc><wait>",
    "install <wait>",
    "auto=true priority=critical file=/mnt/cdrom2/preseed.cfg <wait>",
    "<wait><enter><wait5>",
    "<leftAltOn><f2><leftAltOff>",
    "<wait><enter><wait>",
    "mkdir /mnt/cdrom2<enter><wait>",
    "mount /dev/sr1 /mnt/cdrom2<enter><wait>",
    "<leftAltOn><f1><leftAltOff><wait>",    "<enter><wait>"
  ]
  headless = true
}

build {
  sources = ["source.vmware-iso.debian"]
}
