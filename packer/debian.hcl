variable "ssh_password" {
  description = "Password for the SSH user"
  type        = string
  sensitive   = true
}

source "vmware-iso" "debian" {
  iso_url      = "http://cdimage.debian.org/debian-cd/current/i386/iso-cd/debian-11.0.0-i386-netinst.iso"
  iso_checksum = "file:http://cdimage.debian.org/debian-cd/current/i386/iso-cd/SHA512SUMS"
  iso_checksum_type = "sha512"
  ssh_username = "debian"
  ssh_password = var.ssh_password
  ssh_port     = 22
  ssh_wait_timeout = "10000s"
  shutdown_command = "echo 'debian' | sudo -S shutdown -P now"
  vm_name     = "packer-debian"
  cpus        = 1
  memory      = 1024
  disk_size   = 4096
  format      = "ovf"
  http_directory = "http"
  boot_wait = "10s"
  boot_command = [
    "<esc><wait>",
    "install <wait>",
    "preseed/url=http://{{ .HTTPIP }}:{{ .HTTPPort }}/preseed.cfg <wait>",
    "<enter><wait>"
  ]
  headless = false
}

build {
  sources = ["source.vmware-iso.debian"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y openssh-server",
      "echo 'debian:${var.ssh_password}' | sudo chpasswd"
    ]
  }
}
    