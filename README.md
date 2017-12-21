# Docker container for HBP-Lucene/Solr #

Copyright (c) 2017-2018 2017 [DIAS](https://dias.epfl.ch/BrainDB) laboratory

---

This project creates a lightweight Docker image of a customized *Lucene/Solr* implementation ([HBP-Lucene/Solr](https://bitbucket.org/sakurad/hbp-lucene-solr)) for running HBP Spatial Search Service (API).

---

## Quick-start ##

**1. Clone this project**  
```sh
$ git clone git@bitbucket.org:sakurad/hbp-lucene-solr-docker.git
$ cd hbp-lucene-solr-docker
```

**2. Clone the HBP-Lucene/Solr sources and build it**  
```sh
$ git clone git@bitbucket.org:sakurad/hbp-lucene-solr.git src/hbp-lucene-solr
$ cd src/hbp-lucene-solr && ant compile && cd solr && ant package && cd ../../../
```  

**3. Build the docker image**  
```sh
$ docker build -t hpb-lucene-solr \
#   --build-arg JOBS=8 \
    --build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
    --build-arg VCS_REF=`git -C ./src/ rev-parse --short HEAD` \
    .
```

**_Note:_**

* If you update the sources, add `--no-cache=true` to the command above to take the new version in consideration.
* Option `-t , --tag list`: Name and optionally a tag in the 'name:tag' format
* Replace the `8` in `JOBS=8` with the number of CPU threads to reduce the build time on your machine.

**4. Use the built image**  
```sh
$ docker run --rm --name my-hbp-solr -d -p 8983:8983 hbp-lucene-solr
```

## Using a custom `SOLR_HOME` (outside container)  ##
---

To use a custom *Solr home* directory directory on the host system (outside the container), we can employ a `SOLR_HOME` environment variable by setting it to the desired location (which is now inside the container in its default location at `/opt/hbp-lucene-solr/server/solr`). We support this in hbp-lucene-solr-docker, in combination with volumes:  
```sh
docker run -it -v $PWD/mysolrhome:/mysolrhome -e SOLR_HOME=/mysolrhome hbp-lucene-solr
```

This does need a pre-configured directory at that location (`/mysolrhome`).

As such, hbp-lucene-solr-docker supports a `INIT_SOLR_HOME` setting, which 
copies the contents from the default directory in the image to the `SOLR_HOME` 
(the newly specified must be empty).  
```sh
$ mkdir -p docker-volumes/hbp-solr1
$ sudo chown 8983:8983 docker-volumes/hbp-solr1
$ docker run -it -v $PWD/docker-volumes/hbp-solr1:/hbp-solr1 \
             -e SOLR_HOME=/hbp-solr1 -e INIT_SOLR_HOME=yes \
             hbp-lucene-solr
```

## Putting it all together ##
---

The following is used to run the Spatial Search API in production mode:  
```sh
$ mkdir -p docker-volumes/hbp-solr1
$ sudo chown 8983:8983 docker-volumes/hbp-solr1
$ docker run \
  --name my-hbp-solr \
  -d \
  -p 8983:8983 \
  -it \
  -v $PWD/docker-volumes/hbp-solr1:/hbp-solr1 \
  -e SOLR_HOME=/hbp-solr1 \
  -e INIT_SOLR_HOME=yes \
  -e SOLR_HEAP=12g \
  hbp-lucene-solr
```

Note increased memory size (12GB).

