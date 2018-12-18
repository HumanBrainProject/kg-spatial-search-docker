: ${SHOW_SETTINGS:=false}

#############################################################################
# Global settings
: ${COMPOSE_PROJECT_NAME:="kg"}

#############################################################################
# Global settings
: ${KG_SPATIAL_SEARCH_IMAGE:="solr"}
: ${KG_SPATIAL_SEARCH_VERSION:=":7.4-alpine"}
: ${KG_SPATIAL_SEARCH_PORT:="8983"}
: ${KG_SPATIAL_SEARCH_DATA:="${PWD}/solr"}
: ${KG_SPATIAL_SEARCH_DATA_DEFAULTS:="${PWD}/defaults/basic"}
: ${KG_SPATIAL_SEARCH_HEAP_SIZE:="7g"}
: ${KG_SPATIAL_SEARCH_SERVICE_NAME:="${COMPOSE_PROJECT_NAME}_spatial-search_1"}
: ${KG_SPATIAL_SEARCH_BASE:="solr"}
: ${KG_SPATIAL_SEARCH_URL:="http://localhost:${KG_SPATIAL_SEARCH_PORT}/${KG_SPATIAL_SEARCH_BASE}"}
: ${KG_CONF_FILE_JETTY:="${PWD}/config/jetty.xml"}
: ${KG_CONF_FILE_CONTEXT:="${PWD}/config/solr-jetty-context.xml"}

#############################################################################
# Build settings
: ${KG_SPATIAL_SEARCH_SRC:="git@github.com:HumanBrainProject/kg-spatial-search"}
: ${KG_SPATIAL_SEARCH_NO_CACHE:="true"} # Assume the sources have changed.
