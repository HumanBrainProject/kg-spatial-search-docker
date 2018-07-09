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

FROM openjdk:jdk-alpine as builder
MAINTAINER Lionel Sambuc <lionel.sambuc@epfl.ch>

ENV LANG=C.UTF-8
ENV PREFIX=/opt/kg-spatial-search
ENV SOLR_VERSION="8.0.0" \
    PATH="$PREFIX/bin:$PREFIX/scripts:$PATH"

RUN apk update && \
    apk add git apache-ant perl

COPY src/kg-spatial-search /src

RUN cd /src && \
    ant ivy-bootstrap

RUN cd /src/solr && \
    ant compile && \
    ant package

################################################################################
FROM openjdk:jre-alpine

# Note: All environment variables are resetted by the FROM:
ENV LANG=C.UTF-8
ENV PREFIX=/opt/kg-spatial-search
ENV SOLR_USER="solr" \
    SOLR_UID="8983" \
    SOLR_GROUP="solr" \
    SOLR_GID="8983" \
    SOLR_VERSION="8.0.0" \
    PATH="$PREFIX/bin:$PREFIX/scripts:$PATH" \
    SOLR_HOME="$PREFIX/server/solr"

RUN addgroup -S -g $SOLR_GID $SOLR_GROUP && \
    adduser -S -u $SOLR_UID -G $SOLR_GROUP $SOLR_USER

RUN apk update && \
    apk add bash

COPY --from=builder /src/solr/build/solr-8.0.0-SNAPSHOT/ $PREFIX
COPY scripts $PREFIX/scripts

RUN chown -R $SOLR_USER:$SOLR_GROUP $PREFIX
RUN chmod ugo+x $PREFIX/bin/solr $PREFIX/bin/*.sh $PREFIX/bin/init.d/*

ARG BUILD_DATE
ARG VCS_REF
LABEL org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="kg-spatial-search" \
    org.label-schema.description="Docker image for running the KnowledgeGraph Spatial Search service" \
    org.label-schema.url="https://github.com/HumanBrainProject/kg-spatial-search-docker" \
    org.label-schema.vcs-type="git" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/HumanBrainProject/kg-spatial-search-docker" \
    org.label-schema.vendor="DIAS EPFL" \
    org.label-schema.docker.dockerfile="Dockerfile" \
    org.label-schema.schema-version="0.8"

################################################################################

WORKDIR $PREFIX
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
# CMD ["solr", "start", "-p", "8983", "-f", "-s", "server/solr" ]
#
# The docker image can be run then using:
# ```sh
# docker run --rm --name my-hbp-solr -p 8983:8983 -it kg-spatial-search
# ```
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

