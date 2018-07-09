#!/bin/bash
# -----------------------------------------------------------------------------
#
# Bash script for creating and (re-) deploying Docker container.
#
# -----------------------------------------------------------------------------

# Options for fetching kg-spatial-search source files
: ${SRC:="https://github.com/HumanBrainProject/kg-spatial-search.git"}

# Options for image building
: ${TAG:="kg-spatial-search"}
: ${NOW:=`date -u +"%Y-%m-%dT%H:%M:%SZ"`}
: ${REF:=`git -C ./src/ rev-parse --short HEAD`}
: ${NOCACHE:="true"} # eps., if sources were updated

# Options
: ${MEM:="7g"}; # memory for JVM
: ${ENV:="-e SOLR_HOME=/opt/custom-solr-home-1 -e SOLR_HEAP=${MEM}"}
: ${SOLR_VOLUME:="${PWD}/docker-volumes/custom-solr-home-1"}
: ${POR:="8983:8983"} # port

build_opts="-t ${TAG} --no-cache=${NOCACHE} --build-arg BUILD_DATE=${NOW} --build-arg VCS_REF=${REF}"
run_opts="-d -p ${POR} -v ${SOLR_VOLUME}:/opt/custom-solr-home-1 ${ENV} -e INIT_SOLR_HOME=\${init_solr_home} ${TAG}"; # '-it'

echo "--> HBP KnowledgeGraph Spatial Search Docker image: what do you want to do? <--"
select cmd in "Clone" "Build" "Run" "Resume" "Stop" "Cancel";
do
	case $cmd in
	Clone)
		echo "Clone: get the source code"
		git clone ${SRC} "src/${TAG}"
		break;;

	Build)
		echo "Build: create docker image"
		docker build ${build_opts} .
		break;;

	Run)
		echo "(Clean) run: initialize SOLR_HOME directory and run"
		init_solr_home="yes"
		eval docker run ${run_opts}
		break;;

	Resume)
		echo "Resume: run (new) container using previous SOLR_HOME "
		init_solr_home="no"
		if [ ! -f "${SOLR_VOLUME}/solr.xml" ];
		then # This is a minimum requirement:
			echo "ERROR: 'solr.xml' not found in ${SOLR_VOLUME}!"
			echo "Exiting.."
			exit 1
		fi
		eval docker run ${run_opts}
		break;;

	Stop)
		echo "Stop: halt all running containers"
		cids=`docker ps -aq`
		docker stop ${cids}
		break;;

	Cancel)
		break;;
esac
done

exit 0
