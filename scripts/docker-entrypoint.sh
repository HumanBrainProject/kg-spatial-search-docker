#!/bin/bash
#
# docker-entrypoint for kg-spatial-search
set -e
# From bash set manual:
# -e  Exit immediately if a simple command exits with a non-zero status, unless
#     the command that fails is part of an until or  while loop, part of an if 
#     statement, part of a && or || list, or if the command's return status is 
#     being inverted using !.  -o errexit

if [[ "$VERBOSE" = "yes" ]]; then
    set -x
fi

# when invoked with e.g.: docker run kg-spatial-search -help
if [ "${1:0:1}" = '-' ]; then
    set -- hbp-solr-foreground "$@"
# From bash set manual:
# --  If no arguments follow this option, then the positional parameters are unset. 
#     Otherwise, the positional parameters are set to the arguments, even if 
#     some of them begin with a `-'.
fi

# execute command passed in as arguments.
#

# The Dockerfile has specified the PATH to include
# /opt/kg-spatial-search/bin (for Solr) and
# /opt/kg-spatial-search/scripts (for our scripts like
# solr-foreground, solr-create, solr-precreate, solr-demo).  Note: if
# you specify "solr", you'll typically want to add -f to run it in the
# foreground.
exec "$@"
