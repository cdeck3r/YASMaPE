#!/bin/sh

#
# Generate rulegraphs for snakemake files as .dot files.
# Afterwards, submit to https://quickchart.io/documentation/graphviz-api/
#

# this directory is the script directory
SCRIPT_DIR="$(
    cd "$(dirname "$0")" || exit
    pwd -P
)"
cd "$SCRIPT_DIR" || exit
# shellcheck disable=SC2034
SCRIPT_NAME=$0

# Variables
QUICK_CHART_URL="https://quickchart.io/graphviz?format=svg&graph="

# Main program

# graph for initializing ludwig's yaml files
snakemake -s setupyaml.sk --config symbol="MUX.DE" --rulegraph > setupyaml.dot
snakemake --config symbol="MUX.DE" yaml="regression_return.yaml" --rulegraph -R experiment > experiment.dot
snakemake --config symbol="MUX.DE" yaml="regression_return.yaml" --rulegraph -R evaluate > evaluate.dot
snakemake --config symbol="MUX.DE" yaml="regression_return.yaml" --rulegraph -R predict > predict.dot

# download svg graph from quickchart
DOT_FILE="$(cat setupyaml.dot | tr '\r\n' ' ')"
QUICK_CHART_URL_DOWNLOAD="${QUICK_CHART_URL}${DOT_FILE}"
wget --no-check-certificate -q -nv --show-progress "${QUICK_CHART_URL_DOWNLOAD}" -O setupyaml.svg

DOT_FILE="$(cat experiment.dot | tr '\r\n' ' ')"
QUICK_CHART_URL_DOWNLOAD="${QUICK_CHART_URL}${DOT_FILE}"
wget --no-check-certificate -q -nv --show-progress "${QUICK_CHART_URL_DOWNLOAD}" -O experiment.svg

DOT_FILE="$(cat evaluate.dot | tr '\r\n' ' ')"
QUICK_CHART_URL_DOWNLOAD="${QUICK_CHART_URL}${DOT_FILE}"
wget --no-check-certificate -q -nv --show-progress "${QUICK_CHART_URL_DOWNLOAD}" -O evaluate.svg

DOT_FILE="$(cat predict.dot | tr '\r\n' ' ')"
QUICK_CHART_URL_DOWNLOAD="${QUICK_CHART_URL}${DOT_FILE}"
wget --no-check-certificate -q -nv --show-progress "${QUICK_CHART_URL_DOWNLOAD}" -O predict.svg

# cleanup
rm -rf *.dot

exit 0
