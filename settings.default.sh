: ${SHOW_SETTINGS:=false}

#############################################################################
# Global settings
: ${COMPOSE_PROJECT_NAME:="kg"}
: ${SPATIAL_SEARCH_HOME:?"SPATIAL_SEARCH_HOME IS UNSET, exiting..."}
: ${PROJECT_BIN:="${SPATIAL_SEARCH_HOME}/bin"}
: ${PYTHON_ROOT:="${SPATIAL_SEARCH_HOME}/py-solr"}
PYTHONPATH="${PYTHONPATH}:${PYTHON_ROOT}" # Add to the Python PATH, even if it is empty...

#############################################################################
# Global settings
: ${KG_SPATIAL_SEARCH_IMAGE:="solr"}
: ${KG_SPATIAL_SEARCH_VERSION:=":7.4-alpine"}
: ${KG_SPATIAL_SEARCH_PORT:="8983"}
: ${KG_SPATIAL_SEARCH_DATA:="${SPATIAL_SEARCH_HOME}/solr"}
: ${KG_SPATIAL_SEARCH_DATA_DEFAULTS:="${SPATIAL_SEARCH_HOME}/defaults/basic"}
: ${KG_SPATIAL_SEARCH_HEAP_SIZE:="7g"}
: ${KG_SPATIAL_SEARCH_SERVICE_NAME:="${COMPOSE_PROJECT_NAME}_spatial-search_1"}
: ${KG_SPATIAL_SEARCH_BASE:="solr"}
: ${KG_SPATIAL_SEARCH_URL:="http://localhost:${KG_SPATIAL_SEARCH_PORT}/${KG_SPATIAL_SEARCH_BASE}"}
: ${KG_CONF_FILE_JETTY:="${SPATIAL_SEARCH_HOME}/config/jetty.xml"}
: ${KG_CONF_FILE_CONTEXT:="${SPATIAL_SEARCH_HOME}/config/solr-jetty-context.xml"}

#############################################################################
# Build settings
: ${KG_SPATIAL_SEARCH_SRC:="git@github.com:HumanBrainProject/kg-spatial-search"}
: ${KG_SPATIAL_SEARCH_NO_CACHE:="true"} # Assume the sources have changed.
