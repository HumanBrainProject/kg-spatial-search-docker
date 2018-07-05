#!/bin/bash
# -----------------------------------------------------------------------------
#
# Bash script for creating and (re-) deploying Docker container.
#
# -----------------------------------------------------------------------------

# Options for fetching HBP-Lucene-Solr source files
: ${SRC:="https://github.com/HumanBrainProject/kg-spatial-search.git"};

# Options for image building
: ${TAG:="kg-spatial-search"};
: ${NOW:=`date -u +"%Y-%m-%dT%H:%M:%SZ"`};
: ${REF:=`git -C ./src/ rev-parse --short HEAD`};
: ${NOCACHE:="--no-cache=true"}; # eps., if sources were updated

# Options for clean-run
: ${MEM:="7g"}; # memory for JVM
: ${NAM:="kg-spatial-search"};
: ${INIT_SOLR_HOME:="no"};
: ${ENV:="-e SOLR_HOME=/opt/custom-solr-home-1 -e SOLR_HEAP=${MEM}"};
: ${SOLR_VOLUME:="${PWD}/docker-volumes/custom-solr-home-1"}
: ${POR:="8983:8983"}; # port
# --name ${NAM}

# Options for (re)-run using previous SOLR_HOME
: ${NOINIT:="INIT_SOLR_HOME=no"};

build_opts="-t ${TAG} ${NOCACHE} --build-arg BUILD_DATE=${NOW} --build-arg VCS_REF=${REF}";
run_opts="-d -p ${POR} -v ${SOLR_VOLUME}:/opt/custom-solr-home-1 ${ENV} -e INIT_SOLR_HOME=\${INIT_SOLR_HOME} ${TAG}"; # '-it'

echo "--> HBP KnowledgeGraph Spatial Search Docker image: what do you want to do? <--"
select cmd in "Clone" "Build" "Run" "Resume" "Stop" "Cancel"; do
case $cmd in
  Clone ) echo "Clone: get the source code and compile it" ;
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
        INIT_SOLR_HOME="yes" ;
              eval echo "docker run ${run_opts}" ;
              #eval docker run ${run_opts} ;
              break ;;

  Resume ) echo "Resume: run (new) container using previous SOLR_HOME " ;
           if [ ! -f "${SOLR_VOLUME}/solr.xml" ]; then
             # This is a minimum requirement:
             echo "ERROR: 'solr.xml' not found in ${SOLR_VOLUME}!" ;
             echo "Exiting.." ;
           #  exit ;
           fi
           eval echo "docker run ${run_opts}" ;
           #eval docker run ${rerun_opts} ;
           break ;;

  Stop ) echo "Stop: halt all running containers" ;
          cids=`docker ps -aq` ;
          echo "docker stop ${cids}" ;
          docker stop ${cids} ;
          break ;;

  Cancel )  exit ;;
esac
done

