#!/bin/bash
set -e

#
# Start the celery worker for download_stock_data
#

# this directory is the script directory
SCRIPT_DIR="$(
    cd "$(dirname "$0")" || exit
    pwd -P
)"
cd "$SCRIPT_DIR" || exit
# shellcheck disable=SC2034
SCRIPT_NAME=$0

# variables
LOGLEVEL="INFO"
LOGFILE="/YASMaPE/log/download_stock_data.log"

touch "${LOGFILE}"
[[ -f "${LOGFILE}" ]] || { echo "ERROR: Logfile does not exist: ${LOGFILE}"; echo "Abort."; exit 1; }

# Start the worker
celery -A worker worker --hostname w1@%n --loglevel "${LOGLEVEL}" --logfile "${LOGFILE}" -E
