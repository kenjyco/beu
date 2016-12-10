#!/usr/bin/env bash

[[ ! -d "venv" ]] && python3 -m venv venv && venv/bin/pip3 install wheel
venv/bin/pip3 install pip --upgrade
venv/bin/pip3 install -r requirements.txt --upgrade
