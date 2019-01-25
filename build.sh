#!/bin/sh

: ${SPATIAL_SEARCH_HOME:="${PWD}"}
. ${SPATIAL_SEARCH_HOME}/settings.sh

cd build

if [ ! -d src ]
then
	git clone ${KG_SPATIAL_SEARCH_SRC} src
fi

docker build -t kg-spatial-search \
       --build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
       --build-arg VCS_REF=`git -C ./src/ rev-parse --short HEAD` \
       --no-cache=${KG_SPATIAL_SEARCH_NO_CACHE}
       .
