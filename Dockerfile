################################################################################
#
#                    Copyright (c) 2017-2018
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
# DISCLAIM ANY LIABILITY OF ANY KIND FOR ANY DAMAGES WHATSOEVER RESULTING FROM 
# THE USE OF THIS SOFTWARE.
#
################################################################################

FROM openjdk:jre-alpine
MAINTAINER Darius Sidlauskas <darius.sidlauskas@epfl.ch>

RUN apk update && \
    apk add tar bash

ENV LANG=C.UTF-8
ENV SOLR_USER="solr" \
    SOLR_UID="8983" \
    SOLR_GROUP="solr" \
    SOLR_GID="8983" \
    SOLR_VERSION="8.0.0" \
    PATH="/opt/hbp-lucene-solr/bin:/opt/hbp-lucene-solr-docker/scripts:$PATH"

RUN addgroup -S -g $SOLR_GID $SOLR_GROUP && \
    adduser -S -u $SOLR_UID -G $SOLR_GROUP $SOLR_USER

COPY src/hbp-lucene-solr/solr/package/solr-8.0.0-SNAPSHOT.tgz /opt/hbp-lucene-solr.tgz
RUN mkdir -p /opt/hbp-lucene-solr && \
  tar -C /opt/hbp-lucene-solr --extract --file /opt/hbp-lucene-solr.tgz --strip-components=1 && \
  rm /opt/hbp-lucene-solr.tgz* && \
  rm -Rf /opt/hbp-lucene-solr/docs/
RUN chown -R $SOLR_USER:$SOLR_GROUP /opt/hbp-lucene-solr

COPY scripts /opt/hbp-lucene-solr-docker/scripts
RUN chown -R $SOLR_USER:$SOLR_GROUP /opt/hbp-lucene-solr-docker

#RUN cd /opt/hbp-lucene-solr && ant ivy-bootstrap && ant compile
#RUN cd solr && ant server && ant dist

################################################################################

# FROM openjdk:jre-alpine
# Note: All environment variables are resetted by the FROM:
ENV SOLR_HOME="/opt/hbp-lucene-solr/server/solr"

ARG BUILD_DATE
ARG VCS_REF
LABEL org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="lucene-solr" \
    org.label-schema.description="Docker image for running hbp-lucene-solr" \
    org.label-schema.url="https://bitbucket.org/sakurad/hbp-lucene-solr-docker" \
    org.label-schema.vcs-type="git" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://bitbucket.org/sakurad/hbp-lucene-solr-docker" \
    org.label-schema.vendor="DIAS EPFL" \
    org.label-schema.docker.dockerfile="Dockerfile" \
    org.label-schema.schema-version="0.8"

################################################################################

WORKDIR /opt/hbp-lucene-solr
USER $SOLR_USER
EXPOSE 8983

# Both the ENTRYPOINT and CMD instructions support two different forms: the 
# shell form and the exec form. When using the shell form, the specified binary
# is executed with an invocation of the shell using `/bin/sh -c`.
# When the exec form of the ENTRYPOINT/CMD instruction is used the command will
# be executed without a shell.
#
# Therefore, it is always recommended to use the *exec* form of the 
# ENTRYPOINT/CMD instructions which looks like this:
#   CMD ["executable","param1","param2"]
# instead of *shell* form, which looks like this:
#   CMD executable param1 param2
#
# The next CMD alone worked fine for running a single Solr instance within a 
# docker:
#CMD ["solr", "start", "-p", "8983", "-f", "-s", "server/solr" ]
#
# The docker image can be run then using:
#   `docker run --rm --name my-hbp-solr -d -p 8983:8983 -t hbp-lucene-solr`
#
#
# However, to have more flexibility and following existing conventions, it was
# replaced by the bellow combination of ENTRYPOINT and CMD instructions.
#
# When both an ENTRYPOINT and CMD are specified, the CMD string(s) will be
# appended to the ENTRYPOINT in order to generate the container's command 
# string. Remember that the CMD value can be easily overridden by supplying one
# or more arguments to `docker run` after the name of the image.

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["hbp-solr-foreground"]

