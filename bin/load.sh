#!/bin/sh

: ${SPATIAL_SEARCH_HOME:="${PWD}"}
. ${SPATIAL_SEARCH_HOME}/settings.sh

folder=$(echo load.$(date +%Y%m%d-%H%M))
mkdir -p $folder

iterate() {
	for f in '' $*
	do
		for d in 1 2 5
		do
			echo "points/OIDS,OIDs,total points,time [ms],real,user,sys" \
				| tee ${folder}/$d${f}k.csv
			echo -n "1000,$d${f},$d${f}000," \
				| tee -a ${folder}/$d${f}k.csv
			(time ${PROJECT_BIN}/create-db.sh \
				$d${f}k \
				datasets/$d${f}k.json \
				| grep -o '[0-9.]*' \
			) 2>&1 | cut -f 2 |xargs echo | tr ' ' ',' \
			| tee -a ${folder}/$d${f}k.csv
			echo ------------------------------------------------------------------------
		done
	done
}

if [ ! -e datasets ]
then
	ln -s $(ls -d data*|tail -n 1) datasets
fi

iterate 0 00 000 0000
