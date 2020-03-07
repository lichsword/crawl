#!/bin/bash

set -e

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

function check_for_py_2_and_3() {
    command -v python2 >/dev/null || { echo "No python 2 found"; exit 1; }
    command -v python3 >/dev/null || { echo "No python 3 found"; exit 1; }
}

function compile_requirements() {
    local version="py$1"
    pip install pip-tools
    pip-compile --output-file "requirements/dev.${version}.txt" requirements.in/dev.txt
    pip-compile --output-file "requirements/base.${version}.txt" requirements.in/base.txt
}

function make_venvs () {
    python2 -m virtualenv "${TEMP_DIR}/venv2/"
    python3 -m venv "${TEMP_DIR}/venv3/"
}

function compile_in_venv () (
    local version="$1"
    source ${TEMP_DIR}/venv${version}/bin/activate
    compile_requirements "${version}"
)

function main() {
    check_for_py_2_and_3
    make_venvs
    compile_in_venv 2
    compile_in_venv 3
}

main
