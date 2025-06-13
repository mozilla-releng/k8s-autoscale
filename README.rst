====================
Kubernetes Autoscale
====================

Autoscale scriptworkers in Kubernetes

* Free software: MPL2
* Documentation: https://scriptworker-scripts.readthedocs.io/en/latest/scriptworkers-autoscaling.html

==========
Deployment
==========

Push to `dev` to deploy to dev, and `production` to deploy to production.

Pushes to `main` will build and push images to Dockerhub, but will not perform any deployments. This is useful for ensuring image building/pushing works before attempting a deployment.
