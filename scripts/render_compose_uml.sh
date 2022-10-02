#!/bin/bash
set -e

# Render docker-compose files as UML diagrams

# this directory is the script directory
SCRIPT_DIR="$(
    cd "$(dirname "$0")" || exit
    pwd -P
)"
cd "$SCRIPT_DIR" || exit
# shellcheck disable=SC2034
SCRIPT_NAME=$0

source "${SCRIPT_DIR}/../.env"

docker run --rm -it --name dcv -v "${VOL_DIR}":/input pmsipilot/docker-compose-viz render -m image --force docker-compose.yml --output-file=docker-compose.png --no-networks --no-volumes 