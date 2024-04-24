#!/bin/sh
set -e

export
test $DOCKER_REPO
test $MOZ_FETCHES_DIR
test $SECRET_URL
test $TASKCLUSTER_ROOT_URL
test $TASK_ID
test $VCS_HEAD_REPOSITORY
test $VCS_HEAD_REV
test $DRYRUN

cd $MOZ_FETCHES_DIR
unzstd image.tar.zst

echo "=== Inserting version.json into image ==="
# Create an OCI copy of image in order umoci can patch it
skopeo copy docker-archive:image.tar oci:k8s_autoscale:final

cat > version.json <<EOF
{
    "commit": "${VCS_HEAD_REV}",
    "version": "${APP_VERSION}",
    "source": "${VCS_HEAD_REPOSITORY}",
    "build": "${TASKCLUSTER_ROOT_URL}/tasks/${TASK_ID}"
}
EOF

umoci insert --image k8s_autoscale:final version.json /app/version.json

if [ $DRYRUN = 1 ];
then
    echo "Skipping push because DRYRUN is 1"
else
    echo "=== Generating dockercfg ==="
    install -m 600 /dev/null $HOME/.dockercfg
    curl $SECRET_URL | jq '.secret.dockercfg' > $HOME/.dockercfg

    echo "=== Pushing to docker hub ==="
    DOCKER_TAG="${DOCKER_TAG}-$(cat ./version.txt)-$(date +%Y%m%d%H%M%S)-${GIT_HEAD_REV}"
    skopeo copy oci:k8s_autoscale:final docker://$DOCKER_REPO:$DOCKER_TAG
    skopeo inspect docker://$DOCKER_REPO:$DOCKER_TAG
fi

echo "=== Clean up ==="
rm -rf $HOME/.docker
