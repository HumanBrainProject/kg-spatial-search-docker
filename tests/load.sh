#!/bin/sh

iterate() {
	for f in '' $*
	do
		for d in 1 2 5
		do
			(cd ..; time ./create-db.sh $d${f}k ./tests/datasets/$d${f}k.json)
			echo Loaded 1000 points/OIDS, $d$f OIDs, total $d${f}000 points
			echo ------------------------------------------------------------------------
		done
	done
}

if [ ! -e datasets ]
then
	ln -s $(ls -d data*|tail -n 1) datasets
fi

iterate 0 00 000 0000
