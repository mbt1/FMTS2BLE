#!/bin/bash

##Update both ~/.ssh/known_hosts and ~/.ssh/config for new hosts

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
pushd "$script_dir"

rsync -avz --progress . piw002:~/development/USB2FTMSBLE


popd