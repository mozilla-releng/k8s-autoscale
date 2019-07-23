# -*- coding: utf-8 -*-

"""Console script for kubernetes_autoscaler_for_taskcluster_scriptworkers."""
import sys
import time

import click

from k8s_autoscale.main import autoscale


@click.command()
@click.option(
    "--config", default="config.yaml", help="autoscale config", type=click.File()
)
def main(config):
    """Console script for kubernetes_autoscaler_for_taskcluster_scriptworkers."""
    while True:
        autoscale(config)
        time.sleep(30)
