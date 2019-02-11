#!/bin/sh

: ${SPATIAL_SEARCH_HOME:="${PWD}"}
. ${SPATIAL_SEARCH_HOME}/settings.sh

folder=$(echo queries-parallel-inter-query.$(date +%Y%m%d-%H%M))
mkdir -p $folder

iterate() {
	for f in '' $*
	do
		for d in 1 2 5
		do
			time ${PYTHON_ROOT}/queries-parallel-inter-query-bench.py \
				-c $d${f}k -r 20 -t 10 -u \
				${KG_SPATIAL_SEARCH_URL} | tee ${folder}/$d${f}k.csv
			echo ------------------------------------------------------------------------
		done
	done
}

iterate 0 00 000 0000
