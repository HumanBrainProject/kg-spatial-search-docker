# Docker container for HBP-Lucene/Solr #

Copyright (c) 2016-2018 [DIAS](https://dias.epfl.ch/BrainDB) laboratory

---

This project creates a lightweight Docker image of a customized *Lucene/Solr* implementation ([HBP-Lucene/Solr](https://bitbucket.org/sakurad/hbp-lucene-solr)) for running HBP Spatial Search Service (API).

---

## Quick-start ##

**0. Prerequisites**

First, Java SDK is required for Lucene/Solr compilation:
```sh
$ sudo apt-get update
$ sudo apt-get install default-jdk # On Ubuntu, this will install OpenJDK 8 (the latest and recommended version)
```
Then you need to set `JAVA_HOME` with the path of your preferred installation and set it in `/etc/environment`:
```sh
$ sudo update-alternatives --config java # will list all available Java installations
$ sudo emacs /etc/environment # add 2 lines: "JAVA_HOME=/usr/lib/jvm/default-java/jre" and "export JAVA_HOME"
$ source /etc/environment
```

Also Ant:
```sh
sudo apt-get install ant
```

**1. Clone this project**  
```sh
git clone git@bitbucket.org:sakurad/hbp-lucene-solr-docker.git
cd hbp-lucene-solr-docker
```

**_Note:_** the subsequent steps are automated in `DEPLOY.sh`, except the creation of directories for custom SOLR_HOME:

```sh
# i.e., run:
mkdir -p docker-volumes/custom-solr-home-1 && sudo chown 8983:8983 docker-volumes/custom-solr-home-1`
# before:
./DEPLOY.sh
```

**2. Clone the HBP-Lucene/Solr sources and build it**  
```sh
git clone ssh://git@c4science.ch/source/hbp-lucene-solr.git src/hbp-lucene-solr
# or using https:
git clone https://c4science.ch/source/hbp-lucene-solr.git src/hbp-lucene-solr
cd src/hbp-lucene-solr && ant ivy-bootstrap && ant compile && cd solr && ant package && cd ../../../
```  

**3. Build the docker image**  
```sh
docker build -t hbp-lucene-solr \
    --build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
    --build-arg VCS_REF=`git -C ./src/ rev-parse --short HEAD` \
#   --build-arg JOBS=8 \
    .
```

**_Note:_**

* If you update the sources, add `--no-cache=true` to the command above to take the new version in consideration.
* Option `-t , --tag list`: Name and optionally a tag in the 'name:tag' format
* Replace the `8` in `JOBS=8` with the number of CPU threads to reduce the build time on your machine.

**4. Use the built image**  
```sh
docker run --rm --name my-hbp-solr -d -p 8983:8983 hbp-lucene-solr
```

## Few notes on using a custom `SOLR_HOME` (outside container)  ##
---

To use a custom *Solr home* directory directory on the host system (outside the container), we can employ a `SOLR_HOME` environment variable by setting it to the desired location (which is now inside the container in its default location at `/opt/hbp-lucene-solr/server/solr`). We support this in hbp-lucene-solr-docker, in combination with volumes:  
```sh
docker run -it -v $PWD/mysolrhome:/mysolrhome -e SOLR_HOME=/mysolrhome hbp-lucene-solr
```

This does need a pre-configured directory at that location (`/mysolrhome`).

As such, hbp-lucene-solr-docker supports a `INIT_SOLR_HOME` setting, which 
copies the contents from the default directory in the image to the `SOLR_HOME` 
(the newly specified must be empty).

The following is used to run the Spatial Search API in production mode:  
```sh
mkdir -p docker-volumes/custom-solr-home-1
sudo chown 8983:8983 docker-volumes/custom-solr-home-1
docker run \
  --name my-hbp-solr \
  -d \
  -p 8983:8983 \
  -it \
  -v $PWD/docker-volumes/custom-solr-home-1:/opt/custom-solr-home-1 \
  -e SOLR_HOME=/opt/custom-solr-home-1 \
  -e INIT_SOLR_HOME=yes \
  -e SOLR_HEAP=7g \
  hbp-lucene-solr
```

Note increased memory size (7GB).

**Options used:**

```sh
--name string          Assign a name to the container
-d, --detach           Run container in background and print container ID
-p, --publish list     Publish a container's port(s) to the host
-i, --interactive      Keep STDIN open even if not attached
-t, --tty              Allocate a pseudo-TTY
-v, --volume list      Bind mount a volume
-e, --env list         Set environment variables (within running conmtainer)
```

