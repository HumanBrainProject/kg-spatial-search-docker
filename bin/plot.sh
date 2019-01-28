#!/bin/sh
: ${SPATIAL_SEARCH_HOME:="${PWD}"}
. ${SPATIAL_SEARCH_HOME}/settings.sh

folder=$1
shift
${PYTHON_ROOT}/queries-plot.py $@ $(for f in $(ls ${folder} | cut -d. -f1 | sort -n); do echo ${folder}/${f}.csv; done)
