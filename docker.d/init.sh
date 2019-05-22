#!/bin/bash
set -e
test $CONFIG

exec /app/bin/k8s_autoscale --config /app/configs/$CONFIG
