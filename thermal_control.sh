#!/bin/bash

# source the venv
SCRIPT_PATH=$(dirname "$(realpath "$0")")
. "$SCRIPT_PATH/venv/bin/activate"

# run the python script
python "$SCRIPT_PATH/thermal_control.py"

