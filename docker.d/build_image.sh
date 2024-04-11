#/bin/sh
set -e

test $DOCKER_REPO
test $DOCKER_TAG

docker build -f Dockerfile -t $DOCKER_REPO:$DOCKER_TAG .

docker run -v `pwd`:/workspace --rm -it gcr.io/kaniko-project/executor:latest --dockerfile /workspace/Dockerfile --context dir:///workspace/ --tar-path build.tar --no-push
