#!/bin/sh

: ${SPATIAL_SEARCH_HOME:="${PWD}"}
. ${SPATIAL_SEARCH_HOME}/settings.sh

folder=$(echo datasets.$(date +%Y%m%d-%H%M))
mkdir -p $folder

iterate() {
	for f in '' $*
	do
		for d in 1 2 5
		do
			time ${PYTHON_ROOT}/generate_rnd_uniform.py -o 1000 -p $d$f > $folder/$d${f}k.json
			echo Generated 1000 points/OIDS, $d$f OIDs
			echo ------------------------------------------------------------------------
		done
	done
}

iterate 0 00 000 0000
