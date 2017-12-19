# Docker container for HBP-Lucene-Solr #

(c) 2017 [DIAS](https://dias.epfl.ch/BrainDB) laboratory

---

This project creates a lightweight Docker image for running HBP Spatial Search Service (API) based on .

It has been developed on Ubuntu and not tested on other platforms.

---

## Quick-start ##

**1. Clone this project**  
```sh
$ git clone git@bitbucket.org:sakurad/hbp-lucene-solr-docker.git
```

**2. Clone the HBP-Lucene/Solr sources**  
```sh
$ git clone git@bitbucket.org:sakurad/hbp-lucene-solr.git src
```  

**3. Build the docker image**  
```sh
$ docker build -t hpb-lucene-solr \
    --build-arg JOBS=8 \
    --build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
    --build-arg VCS_REF=`git -C ./src/ rev-parse --short HEAD` \
    .
```

**Note:**

* If you update the sources, add `--no-cache=true` to the command above to take the new version in consideration.
* Option `-t , --tag list`: Name and optionally a tag in the 'name:tag' format
* Replace the `8` in `JOBS=8` with the number of CPU threads to reduce the build time on your machine.

---

## Use the built image ##

To start Spatial Search API service, you will need three folders to store the following files:

1. Lucene index files (actual data)
2. ZooKeeper configuration files
3. Solr configuration files

You can then start the container with the following command:
```sh
$ docker run --rm \
    -e POSTGRES_USER=dbuser \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=db \
    -p 5554:5432 \
    -v $PWD/../data:/data:rw \
    -v $PWD/../datasets:/datasets:ro \
    --name PostgresRAW \
    hbpmip/postgresraw
```
