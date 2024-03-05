#!/bin/bash

##For new hosts:
##Update ~/.ssh/known_hosts
##Example:
# # Host abcde
# #   HostName abcde.local
# #   User auser
# #   IdentityFile ~/.ssh/id_rsa_abcde
##
## Do not update ~/.ssh/config
## restart VSC. Restart of the computer should not be required.

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
pushd "$script_dir"

ssh pi5a001 'mkdir -p ~/development/USB2FTMSBLE'
rsync -avz --progress . pi5a001:~/development/USB2FTMSBLE

popd