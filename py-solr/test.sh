#!/bin/sh

iterate() {
	for f in '' $*
	do
		for d in 1 2 5
		do
			time ./tests.py -c $d${f}k -n 100 -u 'http://M64006A327BAE.dyn.epfl.ch:8983/solr'
			echo ------------------------------------------------------------------------
		done
	done
}

iterate 0 00 000 0000
