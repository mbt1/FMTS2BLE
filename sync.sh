#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
pushd "$script_dir"

rsync -avz --progress . piw001:~/development/USB2FTMSBLE


popd