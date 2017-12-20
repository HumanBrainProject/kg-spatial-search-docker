#!/bin/bash
#
# docker-entrypoint for hbp-solr-lucene-docker
set -e

if [[ "$VERBOSE" = "yes" ]]; then
    set -x
fi

# when invoked with e.g.: docker run solr -help
if [ "${1:0:1}" = '-' ]; then
    set -- solr-foreground "$@"
fi

# execute command passed in as arguments.
#

# The Dockerfile has specified the PATH to include
# /opt/hbp-lucene-solr/bin (for Solr) and
# /opt/hbp-solr-lucene-docker/scripts (for our scripts like
# solr-foreground, solr-create, solr-precreate, solr-demo).  Note: if
# you specify "solr", you'll typically want to add -f to run it in the
# foreground.
exec "$@"
