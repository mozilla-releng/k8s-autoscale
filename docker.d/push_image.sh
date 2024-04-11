#!/bin/sh
set -e

test $DOCKERHUB_EMAIL
test $DOCKERHUB_USER
test $DOCKER_REPO
test $DOCKER_TAG
test $GIT_HEAD_REV
test $PUSH_DOCKER_IMAGE
test $SECRET_URL

if [ "$PUSH_DOCKER_IMAGE" == "0" ]; then
  exit 0
fi

apk -U add jq

echo "=== Loading built image ==="
docker load < build.tar

echo "=== Re-tagging docker image ==="
export DOCKER_ARCHIVE_TAG="${DOCKER_TAG}-$(cat ./version.txt)-$(date +%Y%m%d%H%M%S)-${GIT_HEAD_REV}"
docker tag unset-repo/unset-image-name:latest $DOCKER_REPO:$DOCKER_ARCHIVE_TAG
docker tag unset-repo/unset-image-name:latest $DOCKER_REPO:$DOCKER_TAG

echo "=== Generating dockercfg ==="
# docker login stopped working in Taskcluster for some reason
wget -qO- $SECRET_URL | jq '.secret.docker.dockercfg' > /root/.dockercfg
chmod 600 /root/.dockercfg

echo "=== Pushing to docker hub ==="
docker push $DOCKER_REPO:$DOCKER_TAG
docker push $DOCKER_REPO:$DOCKER_ARCHIVE_TAG

echo "=== Clean up ==="
rm -f /root/.dockercfg
