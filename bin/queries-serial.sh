#!/bin/sh

: ${SPATIAL_SEARCH_HOME:="${PWD}"}
. ${SPATIAL_SEARCH_HOME}/settings.sh

folder=$(echo queries-serial.$(date +%Y%m%d-%H%M))
mkdir -p $folder

iterate() {
	for f in '' $*
	do
		for d in 1 2 5
		do
			time ${PYTHON_ROOT}/queries-serial-bench.py -c $d${f}k -n 20 -u \
				${KG_SPATIAL_SEARCH_URL} | tee ${folder}/$d${f}k.csv
			echo ------------------------------------------------------------------------
		done
	done
}

iterate 0 00 000 0000
