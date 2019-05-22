#/bin/bash

set -xe
commit=$(git rev-parse HEAD)
version=$(cat version.txt)

cat > version.json <<EOF
{
    "commit": "${commit}",
    "version": "${version}",
    "source": "https://github.com/mozilla-releng/k8s-autoscale",
    "build": "https://github.com/mozilla-releng/k8s-autoscale/commit/${commit}"
}
EOF
