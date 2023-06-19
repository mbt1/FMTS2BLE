#!/bin/bash

# requirements:
# - ovftool must be in path (VMWare product, often installed with VMWare)
# - wget must be in path (brew install wget)
# - mkpasswd must be in path (brew install whois)


# Hardcoded URL
iso_url="http://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.0.0-amd64-netinst.iso"
checksums_url="http://cdimage.debian.org/debian-cd/current/amd64/iso-cd/SHA512SUMS"

# Download the checksum file
SHA512SUMS=$(mktemp)
wget -O $SHA512SUMS $checksums_url

# Parse the checksum for the specific iso
iso_checksum=$(grep $(basename $iso_url) $SHA512SUMS | cut -d " " -f1)

# Change to the script's directory
pushd "$(dirname "$BASH_SOURCE")"

# Call Packer
export PACKER_LOG=1
export PACKER_LOG_PATH=packer.log

#!/bin/bash

ssh_password='P@$$w0rd'
# # Prompt for the password
# read -s -p "Enter SSH password: " ssh_password
# echo

# # Confirm the password
# while true; do
#     read -s -p "Confirm password: " password_confirm
#     echo
#     if [ "$ssh_password" = "$password_confirm" ]; then
#         break
#     else
#         echo "Passwords do not match. Please try again."
#     fi
# done

# Create the hash with 2,000,000 rounds and save it in a variable
#hashed_password=$(echo -n "$ssh_password" | python3 -c "import sys; from passlib.hash import sha512_crypt; print(sha512_crypt.using(rounds=5000).hash(sys.stdin.read().strip()))")

# Escape special characters in the hashed password
#hashed_password_escaped=$(printf '%s\n' "$hashed_password" | sed -e 's/[\/&]/\\&/g')

# Create a copy of the template and replace <<PASSWORDHASH>> with the hashed password
sed "s/<<PASSWORDHASH>>/$hashed_password_escaped/g" http/preseed.template.cfg > http/preseed.cfg

packer build -on-error=ask -var "ssh_password=$ssh_password" -var "iso_url=$iso_url" -var "iso_checksum=$iso_checksum" debian.pkr.hcl

# Unset the password variable
unset password

# Return to the previous directory
popd
