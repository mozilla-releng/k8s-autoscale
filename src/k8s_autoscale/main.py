import logging
import os.path
import time

import kubernetes
from redo import retriable
from taskcluster import Queue
from taskcluster.exceptions import TaskclusterRestFailure

from k8s_autoscale.slo import get_target_replica_count

logger = logging.getLogger(__name__)


def autoscale(worker_types):
    while True:
        for worker_type in worker_types:
            # TODO: run in parallel
            handle_worker_type(worker_type)
        logger.info("Sleeping between polls")
        time.sleep(180)


def get_api(kube_config, kube_config_context):
    if kube_config and kube_config_context:
        logger.info("Using kube config")
        api_client = kubernetes.config.new_client_from_config(
            config_file=os.path.expanduser(kube_config), context=kube_config_context
        )
    else:
        logger.info("Using in-cluster config")
        api_client = kubernetes.config.load_incluster_config()
    api = kubernetes.client.AppsV1beta2Api(api_client=api_client)
    return api


def get_deployment_status(api, deployment_namespace, deployment_name):
    return api.read_namespaced_deployment(
        name=deployment_name, namespace=deployment_namespace
    ).status


def get_running(api, deployment_namespace, deployment_name):
    return get_deployment_status(api, deployment_namespace, deployment_name).ready_replicas or 0


def adjust_scale(api, target_replicas, deployment_namespace, deployment_name):
    # "add" works as "replace" in case we have more than 0 replicas.
    # "replace" fails in case we don't have any replicas running
    patch = [{"op": "add", "path": "/spec/replicas", "value": target_replicas}]
    logger.debug("PATCH object: %s", patch)
    api.patch_namespaced_deployment_scale(
        name=deployment_name, namespace=deployment_namespace, body=patch
    )


@retriable(sleeptime=3, max_sleeptime=10, retry_exceptions=(TaskclusterRestFailure,))
def get_pending(queue, provisioner, worker_type):
    return queue.pendingTasks(provisioner, worker_type)["pendingTasks"]


def handle_worker_type(cfg):
    min_replicas = cfg["autoscale"]["min_replicas"]
    log_env = dict(
        worker_type=cfg["worker_type"],
        provisioner=cfg["provisioner"],
        deployment_namespace=cfg["deployment_namespace"],
        deployment_name=cfg["deployment_name"],
        min_replicas=min_replicas,
    )
    api = get_api(cfg.get("kube_connfig"), cfg.get("kube_connfig_context"))
    logger.info("Handling worker type. Getting the number of running replicas...", extra=log_env)
    running = get_running(
        api=api,
        deployment_namespace=cfg["deployment_namespace"],
        deployment_name=cfg["deployment_name"],
    )
    log_env["running"] = running
    logger.info("Calculating capacity", extra=log_env)
    max_replicas = cfg["autoscale"]["max_replicas"]
    min_replicas = cfg["autoscale"]["min_replicas"]
    log_env["max_replicas"] = max_replicas
    log_env["min_replicas"] = min_replicas

    logger.info("Checking pending", extra=log_env)
    queue = Queue({"rootUrl": cfg["root_url"]})
    pending = get_pending(queue, cfg["provisioner"], cfg["worker_type"])
    log_env["pending"] = pending
    logger.info("Calculating target replica count", extra=log_env)
    target_replicas = get_target_replica_count(pending, running, cfg["autoscale"]["args"])
    target_replicas = max(min(target_replicas, max_replicas), min_replicas)
    log_env["target_replicas"] = target_replicas
    if target_replicas == running:
        logger.info("Zero new replicas needed", extra=log_env)
    else:
        if target_replicas < running:
            logger.info(f"Need to remove {running-target_replicas} of {running}", extra=log_env)
        else:
            logger.info(
                f"Need to increase capacity from {running} running by {target_replicas-running}",
                extra=log_env,
            )
        adjust_scale(api, target_replicas, cfg["deployment_namespace"], cfg["deployment_name"])
    logger.info("Done handling worker type", extra=log_env)
