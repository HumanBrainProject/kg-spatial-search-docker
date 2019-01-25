#Settings are taken in the following order of precedence:
#  1. Shell Environment, or on the command line

#  2. Node-specific settings `settings.local.<Alias>.sh`
if test ! -z "$1" && test -f ${SPATIAL_SEARCH_HOME}/settings.local.$1.sh;
then
	. ${SPATIAL_SEARCH_HOME}/settings.local.$1.sh;
fi

#  3. Federation-specific `settings.local.sh`
if test -f ${SPATIAL_SEARCH_HOME}/settings.local.sh;
then
	. ${SPATIAL_SEARCH_HOME}/settings.local.sh;
fi

#  4. Default settings `settings.default.sh`
if test -f ${SPATIAL_SEARCH_HOME}/settings.default.sh;
then
	. ${SPATIAL_SEARCH_HOME}/settings.default.sh;
fi

if ${SHOW_SETTINGS};
then
	echo "Current settings:"
fi

for v in $(grep '^:' ${SPATIAL_SEARCH_HOME}/settings.default.sh|cut -c 5- |cut -d: -f1)
do
	eval "export $v=\"\$$v\""
	if ${SHOW_SETTINGS};
	then
		eval "echo $v=\$$v"
	fi
done

if ${SHOW_SETTINGS};
then
	echo
fi
