import logging
import os.path
import pathlib
import time

import kubernetes
from redo import retriable
from taskcluster.exceptions import TaskclusterRestFailure

from k8s_autoscale.slo import get_new_worker_count
from taskcluster import Queue

logger = logging.getLogger(__name__)


def autoscale(worker_types, healthcheck_file=None):
    while True:
        touch(healthcheck_file)
        for worker_type in worker_types:
            # TODO: run in parallel
            handle_worker_type(worker_type)
            touch(healthcheck_file)
        logger.info("Sleeping between polls")
        time.sleep(15)


def touch(flag_file):
    if not flag_file:
        return
    pathlib.Path(flag_file).touch()


def get_api(kube_config, kube_config_context):
    if kube_config and kube_config_context:
        logger.info("Using kube config")
        api_client = kubernetes.config.new_client_from_config(
            config_file=os.path.expanduser(kube_config), context=kube_config_context
        )
    else:
        logger.info("Using in-cluster config")
        api_client = kubernetes.config.load_incluster_config()
    api = kubernetes.client.AppsV1Api(api_client=api_client)
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
    taskQueueId = provisioner + "/" + worker_type
    return queue.pendingTasks(taskQueueId)["pendingTasks"]


def handle_worker_type(cfg):
    min_replicas = cfg["autoscale"]["args"]["min_replicas"]
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
    capacity = cfg["autoscale"]["args"]["max_replicas"] - running
    log_env["capacity"] = capacity

    logger.info("Checking pending", extra=log_env)
    queue = Queue({"rootUrl": cfg["root_url"]})
    pending = get_pending(queue, cfg["provisioner"], cfg["worker_type"])
    log_env["pending"] = pending
    logger.info("Calculated desired replica count", extra=log_env)
    desired = get_new_worker_count(pending, running, cfg["autoscale"]["args"])
    log_env["desired"] = desired
    if desired == 0:
        logger.info("Zero replicas needed", extra=log_env)
        if running < min_replicas:
            logger.info("Using min_replicas", extra=log_env)
            adjust_scale(api, min_replicas, cfg["deployment_namespace"], cfg["deployment_name"])
        return
    if desired < 0:
        logger.info("Need to remove %s of %s", abs(desired), running, extra=log_env)
        target_replicas = running + desired
        log_env["target_replicas"] = target_replicas
        if target_replicas < 0:
            logger.info("Target is negative, setting to zero", extra=log_env)
            target_replicas = 0
            log_env["target_replicas"] = target_replicas
        if target_replicas < min_replicas:
            logger.info("Using min_replicas instead of target", extra=log_env)
            target_replicas = min_replicas
            log_env["target_replicas"] = target_replicas
        adjust_scale(api, target_replicas, cfg["deployment_namespace"], cfg["deployment_name"])
    else:
        adjustment = min([capacity, desired])
        log_env["adjustment"] = adjustment
        logger.info(
            "Need to increase capacity from %s running by %s", running, adjustment, extra=log_env
        )
        if capacity <= 0:
            logger.info("Maximum capacity reached", extra=log_env)
            return
        adjust_scale(api, running + adjustment, cfg["deployment_namespace"], cfg["deployment_name"])
    logger.info("Done handling worker type", extra=log_env)
