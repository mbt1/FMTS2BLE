#!/bin/bash

# Ask for the password
echo -n "Enter the SSH password: "
read -s ssh_password
echo

# Change to the script's directory
pushd "$(dirname "$BASH_SOURCE")"

# Call Packer
packer build -var "ssh_password=$ssh_password" debian.pkr.hcl

# Return to the previous directory
popd
