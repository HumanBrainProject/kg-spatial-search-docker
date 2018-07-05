#!/bin/bash
# -----------------------------------------------------------------------------
#
# Bash script for creating and (re-) deploying Docker container.
#
# -----------------------------------------------------------------------------

# Options for fetching HBP-Lucene-Solr source files
SRC="https://github.com/HumanBrainProject/kg-spatial-search.git" ;

# Options for image building
TAG="hbp-lucene-solr" ;
NOW=`date -u +"%Y-%m-%dT%H:%M:%SZ"` ;
REF=`git -C ./src/ rev-parse --short HEAD` ;
NOCACHE="--no-cache=true" ; # eps., if sources were updated
build_opts="-t ${TAG} ${NOCACHE} --build-arg BUILD_DATE=${NOW} --build-arg VCS_REF=${REF}" ;

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
select cmd in "Clone" "Build" "Run" "Resume" "Stop" "Cancel"; do
case $cmd in
  Clone ) echo "Clone: get HBP-Lucene-Solr source code and compile it" ;
          echo "git clone ${SRC} src/${TAG}" ;
          git clone ${SRC} "src/${TAG}" ;
          echo "cd src/${TAG} && ant ivy-bootstrap && ant compile" ;
          cd src/${TAG} && ant ivy-bootstrap && ant compile ;
          echo "cd solr && ant package && cd ../../../" ;
          cd solr && ant package && cd ../../../ ;

          break ;;

  Build ) echo "Build: create docker image" ;
          echo "docker build ${build_opts} ." ;
          docker build ${build_opts} . ;
          break ;;

  Run ) echo "(Clean) run: initialize SOLR_HOME directory and run" ;
              echo "docker run ${run_opts}" ;
              docker run ${run_opts} ;
              break ;;

  Resume ) echo "Resume: run (new) container using previous SOLR_HOME " ;
           solr_local_homedir="docker-volumes/custom-solr-home-1" ;
           if [ ! -f "${solr_local_homedir}/solr.xml" ]; then
             # This is a minimum requirement:
             echo "ERROR: 'solr.xml' not found in ${solr_local_homedir}!" ;
             echo "Exiting.." ;
             exit ;
           fi
           echo "docker run ${rerun_opts}" ;
           docker run ${rerun_opts} ;
           break ;;

  Stop ) echo "Stop: halt all running containers" ;
          cids=`docker ps -aq` ;
          echo "docker stop ${cids}" ;
          docker stop ${cids} ;
          break ;;

  Cancel )  exit ;;
esac
done

