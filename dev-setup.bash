#!/usr/bin/env bash

# Get the directory where this script lives
DIR="$(cd "$(dirname "$0")" && pwd)"

CLOUD_INSTANCE=
[[ -d /var/lib/cloud/instance ]] && CLOUD_INSTANCE=yes

[[ ! -d "venv" ]] && python3 -m venv venv && venv/bin/pip3 install --upgrade pip wheel
pip_args=(--upgrade)
pip_version=$(venv/bin/pip3 --version | egrep -o 'pip (\d+)' | cut -c 5-)
[[ -z "$pip_version" ]] && pip_version=$(venv/bin/pip3 --version | perl -pe 's/^pip\s+(\d+).*/$1/')
[[ -z "$pip_version" ]] && pip_version=0
[[ $pip_version -gt 9 ]] && pip_args=(--upgrade --upgrade-strategy eager)
venv/bin/pip3 install -r requirements.txt ${pip_args[@]}
if [[ $(uname) == 'Darwin' ]]; then
    venv/bin/pip3 install ${pip_args[@]} mocp mocp-cli
elif [[ -z "$CLOUD_INSTANCE" ]]; then
    venv/bin/pip3 install ${pip_args[@]} mocp mocp-cli vlc-helper
fi
venv/bin/python3 setup.py develop
