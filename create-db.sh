#!/bin/sh

. ./settings.sh

if [ -z $1 ]
then
	echo "Missing core name."
fi

core=$1
shift

if [ ! -z $1 ]
then
	data="-f $1"
	shift
fi

# 1. Create the core
if [ ! -d ${KG_SPATIAL_SEARCH_DATA}/${core} ]
then
	sudo cp -r ${KG_SPATIAL_SEARCH_DATA_DEFAULTS} ${KG_SPATIAL_SEARCH_DATA}/${core}
	sudo chown -R 8983:8983 ${KG_SPATIAL_SEARCH_DATA}
fi

# 2. Register the Spatial types and fields
./py-solr/register.py -u ${KG_SPATIAL_SEARCH_URL} -c ${core} ${data} $@
