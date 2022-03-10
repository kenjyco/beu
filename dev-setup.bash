#!/usr/bin/env bash

# Get the directory where this script lives
DIR="$(cd "$(dirname "$0")" && pwd)"

CLOUD_INSTANCE=
[[ -d /var/lib/cloud/instance ]] && CLOUD_INSTANCE=yes

cd "$DIR"
pip_args=(--no-warn-script-location --upgrade --upgrade-strategy eager)
PYTHON="python3"
PIP="venv/bin/pip3"
if [[ $(uname) =~ "MINGW" ]]; then
    PYTHON="python"
    PIP="venv/Scripts/pip"
fi
if [[ "$1" == "clean" ]]; then
    rm -rf venv
    find . \( -name __pycache__ -o -name '.eggs' -o -name '*.egg-info' -o -name 'build' -o -name 'dist' \) -print0 |
        xargs -0 rm -rf
fi
[[ ! -d venv ]] && $PYTHON -m venv venv
PYTHON=$(dirname $PIP)/python
$PYTHON -m pip install --upgrade pip wheel
extra_packages=(ipython)
if [[ ! $(uname) =~ "MINGW" ]]; then
    if [[ $(uname) == "Darwin" ]]; then
        extra_packages+=(pdbpp mocp mocp-cli)
    elif [[ -z "$CLOUD_INSTANCE" ]]; then
        extra_packages+=(pdbpp mocp mocp-cli vlc-helper)
    fi
fi
$PIP install ${extra_packages[@]} ${pip_args[@]} --editable .
