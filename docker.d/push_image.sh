#!/bin/sh
set -e
test $SECRET_URL
test $DOCKERHUB_EMAIL
test $DOCKERHUB_USER
test $TAG

apk -U add jq

dockerhub_password=$(wget -qO- $SECRET_URL | jq '.["secret"]["docker"]["password"]')

docker login -e $DOCKERHUB_EMAIL -u $DOCKERHUB_USER -p $dockerhub_password
docker push $TAG

echo "=== Clean up ==="
rm -f /root/.dockercfg
