#!/bin/bash

# requirements:
# - ovftool must be in path (VMWare product, often installed with VMWare)
# - wget must be in path (brew install wget)


# Hardcoded URL
iso_url="http://cdimage.debian.org/debian-cd/current/i386/iso-cd/debian-11.7.0-i386-netinst.iso"
checksums_url="http://cdimage.debian.org/debian-cd/current/i386/iso-cd/SHA512SUMS"

# Download the checksum file
SHA512SUMS=$(mktemp)
wget -O $SHA512SUMS $checksums_url

# Parse the checksum for the specific iso
iso_checksum=$(grep $(basename $iso_url) $SHA512SUMS | cut -d " " -f1)

# Ask for the password
echo -n "Enter the SSH password: "
read -s ssh_password
echo

# Change to the script's directory
pushd "$(dirname "$BASH_SOURCE")"

# Call Packer
export PACKER_LOG=1
export PACKER_LOG_PATH=packer.log

packer build -on-error=ask -var "ssh_password=$ssh_password" -var "iso_url=$iso_url" -var "iso_checksum=$iso_checksum" debian.pkr.hcl

# Return to the previous directory
popd
