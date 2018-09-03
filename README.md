# Docker container for HBP-Lucene/Solr #

This project uses a lightweight Docker image of *Lucene/Solr*, and customize it to run the HBP Spatial Search service.

It also contains build scripts for a customized *Lucene/Solr* implementation ([kg-spatial-search](https://github.com/HumanBrainProject/kg-spatial-search)) in case performance enhancement can't be achieved through configuration.

## Prerequisites

First, install docker, following the official documentation: [Docker Community Edition](https://www.docker.com/community-edition#/download).

While we do try to keep things portable, keep in mind this project has been developped under Linux Ubuntu 16.04 LTS, and provides only UNIX shell scripts.

## Quick-start

1. **Clone this project**

   ```sh
   $ git clone git@github.com:HumanBrainProject/kg-spatial-search-docker
   ```

2. **Sources layout**

   ```
   .
   ├── build
   │   ├── Dockerfile
   │   ├── scripts
   │   └── src               # Only present if a build was attempted, and the sources
   |                         # downloaded
   ├── build.sh
   ├── create-db.sh
   ├── create-release-db.sh
   ├── create-staging-db.sh
   ├── defaults
   │   ├── basic
   │   └── full
   ├── docker-compose.yml
   ├── LICENSE
   ├── py-solr                # Python wrappers and tools around the Solr REST API
   │   ├── __init__.py
   │   ├── register.py        # Convenience command line tool to manage datasets
   │   └── solr.py            # Python wrapper
   ├── README.md
   ├── run.sh
   ├── settings.default.sh
   └── settings.sh
   ```

3. **Start the Solr server**

   Add a file named `settings.local.sh` with the variables set as needed, if the default values from `settings.default.sh` are not suitable for you.

   ```sh
   $ cd kg-spatial-search-docker
   $ ./run.sh up -d # Start the official Docker image of Solr
   ```

4. **Create a dataset**

   You can create the default `release` and `staging` datasets using one of: 

   ```sh
   $ ./create-release-db.sh
   # and/or
   $ ./create-staging-db.sh
   ```

   The datasets will be created with the types required, but empty.

   If you have data which you would like to load at the same time you can do: 

   ```sh
   $ ./create-db.sh <dataset name> <data_file.json>
   # or, if the dataset already exists, you can load data with:
   $ ./create-db.sh <dataset name> <data_file.json> -l
   ```

## Step by Step guide

1. **Clone this project**

   ```sh
   $ git clone git@github.com:HumanBrainProject/kg-spatial-search-docker.git kg-spatial-search-docker
   ```

2. **Clone the kg-spatial-search sources**

   ```sh
   $ git clone https://github.com/HumanBrainProject/kg-spatial-search.git build/src/
   ```

3. **Build the docker image**  

   ```sh
   $ ./build.sh
   ```

   **_Note:_** This allows for building a modified version of Solr. At this time this is not required, and the `run.sh` script uses the official docker image by default. If you wish to use your own version, you will need to set the following as well:

   ```sh
   KG_SPATIAL_SEARCH_IMAGE=<your image tag>
   KG_SPATIAL_SEARCH_VERSION=<the image version to use>
   ```

4. **Use the docker image** 

   The run script calls `docker-compose` with the settings and the docker-compose.yml file of the repository.

   You can use all the regular docker-compose commands as parameters, so for example to start the service:

   ```sh
   $ ./run.sh up -d
   ```

   To stop it, and remove the container, you can use:

   ```sh
   $ ./run.sh down
   ```

5. You can use the python API wrapper provided to create and manage datasets. They are available in `py-solr`

---

## Acknowledgements

This project received funding from the European Union’s Horizon 2020 Framework Programme for Research and Innovation under the Framework Partnership Agreement No. 650003 (HBP FPA).
