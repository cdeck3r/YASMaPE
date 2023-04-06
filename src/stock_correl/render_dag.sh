#!/bin/bash
set -e

# this directory is the script directory
SCRIPT_DIR="$(
    cd "$(dirname "$0")" || exit
    pwd -P
)"
cd "$SCRIPT_DIR" || exit
# shellcheck disable=SC2034
SCRIPT_NAME=$0

# variables
JSON_FILE="payload.json"
PNG_FILE="dag.png"

########################
# Main
########################

#
# 1. Create a snakemake dag (dot format) and escape \n, \t and " chars for using dot in json
# 2. Create json payload file including escaped dag 
# 3. Send json payload to webservice and store result as png file
# 4. Cleanup

# 1.
DAG_JSON=$(snakemake --cores all -npr --dag | sed -z 's/\n/\\n/g;s/\t/\\t/g;s/"/\\"/g')

# 2.
# See https://quickchart.io/documentation/graphviz-api/
cat <<EOF >"${JSON_FILE}"
{
  "graph": "${DAG_JSON}",
  "layout": "dot",
  "format": "png"
}
EOF

# 3. web service generates the images
curl -X POST 'https://quickchart.io/graphviz' -H 'Content-Type: application/json' -d @"${JSON_FILE}" -o "${PNG_FILE}"

# 4. cleanup
rm -rf "${JSON_FILE}"
