import os.path
import time

import kubernetes
import yaml
from k8s_autoscale.logging import get_logger
from k8s_autoscale.sla import get_new_worker_count
from taskcluster import Queue

logger = get_logger()
q = Queue({"rootUrl": "https://taskcluster.net"})


def autoscale(config):
    config = yaml.safe_load(config)
    while True:
        for worker_type in config["worker_types"]:
            # TODO: run in parallel
            handle_worker_type(worker_type)
        time.sleep(30)


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
    return (
        get_deployment_status(api, deployment_namespace, deployment_name).ready_replicas
        or 0
    )


def get_booting(api, deployment_namespace, deployment_name):
    return (
        get_deployment_status(
            api, deployment_namespace, deployment_name
        ).unavailable_replicas
        or 0
    )


def adjust_scale(api, running, adjustment, deployment_namespace, deployment_name):
    # "add" works as "replace" in case we have more than 0 replicas.
    # "replace" fails in case we don't have any replicas running
    patch = [{"op": "add", "path": "/spec/replicas", "value": running + adjustment}]
    logger.debug("PATCH object", patch=patch)
    api.patch_namespaced_deployment_scale(
        name=deployment_name, namespace=deployment_namespace, body=patch
    )


def handle_worker_type(cfg):
    log = logger.bind(worker_type=cfg["name"], provisioner=cfg["provisioner"])
    api = get_api(cfg.get("kube_connfig"), cfg.get("kube_connfig_context"))
    log.info("Handling worker type. Getting the number of running replicas...")
    running = get_running(
        api=api,
        deployment_namespace=cfg["deployment_namespace"],
        deployment_name=cfg["deployment_name"],
    )
    log.bind(running=running)
    log.info("Getting the number of replicas in progress...")
    booting = get_booting(
        api=api,
        deployment_namespace=cfg["deployment_namespace"],
        deployment_name=cfg["deployment_name"],
    )
    log.bind(booting=booting)
    log.info("Calculating capacity")
    capacity = cfg["autoscale"]["args"]["max_replicas"] - (running + booting)
    log.bind(capacity=capacity)
    log.info("Checking capacity")
    if capacity <= 0:
        log.info("Maximum capacity reached")
        return

    log.info("Checking pending")
    pending = q.pendingTasks(cfg["provisioner"], cfg["name"])["pendingTasks"]
    log.bind(pending=pending)
    log.info("Calculated desired replica count")
    desired = get_new_worker_count(pending, running, booting, cfg["autoscale"]["args"])
    log.bind(desired=desired)
    if desired == 0:
        log.info("Zero replicas needed")
        return
    if desired < 0:
        log.info(f"Need to remove {abs(desired)} of {running}")
        adjust_scale(
            api, running, desired, cfg["deployment_namespace"], cfg["deployment_name"]
        )
    else:
        adjustment = min([capacity, desired])
        log.bind(adjustment=adjustment)
        log.info(f"Need to increase capacity from {running} running by {adjustment}")
        adjust_scale(
            api,
            running,
            adjustment,
            cfg["deployment_namespace"],
            cfg["deployment_name"],
        )
    log.info("Done handling worker type")
