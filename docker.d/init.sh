#!/bin/bash
set -e
test $CONFIG

exec /app/.venv/bin/k8s_autoscale --config /app/configs/$CONFIG
