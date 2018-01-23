#!/bin/bash
# -----------------------------------------------------------------------------
#
# Bash script for creating and (re-) deploying Docker container.
#
# -----------------------------------------------------------------------------

# Options for image building
TAG="hbp-lucene-solr" ;
NOW=`date -u +"%Y-%m-%dT%H:%M:%SZ"` ;
REF=`git -C ./src/ rev-parse --short HEAD` ;
build_opts="-t ${TAG} --build-arg BUILD_DATE=${NOW} --build-arg VCS_REF=${REF}" ;

# Options for clean-run
MEM="7g" ; # memory for JVM
NAM="my-hbp-solr" ;
INIT="INIT_SOLR_HOME=yes" ;
ENV="-e SOLR_HOME=/opt/custom-solr-home-1 -e SOLR_HEAP=${MEM}" ;
VOL="$PWD/docker-volumes/custom-solr-home-1:/opt/custom-solr-home-1" ;
POR="8983:8983" ; # port
# --name ${NAM}
run_opts="-d -p ${POR} -v ${VOL} ${ENV} -e ${INIT} ${TAG}" ; # '-it'

# Options for (re)-run using previous SOLR_HOME
NOINIT="INIT_SOLR_HOME=no" ;
rerun_opts="-d -p ${POR} -v ${VOL} ${ENV} -e ${NOINIT} ${TAG}" ; # '-it'

echo "--> HBP Lucene-Solr Docker image: what do you want to do? <--"
select cmd in "Build" "Run" "Resume" "Exit"; do
case $cmd in
  Build ) echo "Build: create docker image" ;
          echo "docker build ${all_options} ." ;
          docker build ${build_opts} . ;
          break ;;

  Run ) echo "(Clean) run: initialize SOLR_HOME directory and run" ;
              echo "docker run ${run_opts}" ;
              docker run ${run_opts} ;
              break;;

  Resume ) echo "Resume: run (new) container using previous SOLR_HOME " ;
           echo "docker run ${rerun_opts}" ;
           docker run ${rerun_opts} ;
           break;;

  Exit )  exit;;
esac
done

