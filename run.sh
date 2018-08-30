#!/bin/sh
#                    Copyright (c) 2018-2018
#   Data Intensive Applications and Systems Labaratory (DIAS)
#            Ecole Polytechnique Federale de Lausanne
#
#                      All Rights Reserved.
#
# Permission to use, copy, modify and distribute this software and its
# documentation is hereby granted, provided that both the copyright notice
# and this permission notice appear in all copies of the software, derivative
# works or modified versions, and any portions thereof, and that both notices
# appear in supporting documentation.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. THE AUTHORS AND ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE
# DISCLAIM ANY LIABILITY OF ANY KIND FOR ANY DAMAGES WHATSOEVER RESULTING FROM THE
# USE OF THIS SOFTWARE.

# Import settings
. ./settings.sh

# Permanent storage
if [ ! -d ${KG_SPATIAL_SEARCH_DATA} ];
then
	mkdir -p ${KG_SPATIAL_SEARCH_DATA}
	sudo chown 8983:8983 ${KG_SPATIAL_SEARCH_DATA}
fi

# Generate Configuration from templates
if false; then
for f in ${CONF_FILE_1}
do
	for v in $(grep '^:' settings.default.sh|cut -c 5- |cut -d: -f1)
	do
		eval "t=\"s#${v}#\${${v}}#g\""
		script="${script}${t};"
		sed -e "${script}" $f.in > $f
	done
done
fi

docker-compose $@
