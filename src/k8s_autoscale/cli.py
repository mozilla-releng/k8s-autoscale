# -*- coding: utf-8 -*-

"""Console script for kubernetes_autoscaler_for_taskcluster_scriptworkers."""
import logging
import os
import sys

import click
import yaml

from k8s_autoscale.logging import configure_logging, configure_sentry
from k8s_autoscale.main import autoscale
from k8s_autoscale.validate import validate


@click.command()
@click.option("--config", default="config.yaml", help="autoscale config", type=click.File())
def main(config):
    """Console script for kubernetes_autoscaler_for_taskcluster_scriptworkers."""
    level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    configure_logging(level)
    if os.environ.get("SENTRY_DSN") and os.environ.get("ENV"):
        configure_sentry(environment=os.environ["ENV"], sentry_dsn=os.environ["SENTRY_DSN"])
    config = yaml.safe_load(config)
    autoscale(config["worker_types"], config.get("healthcheck_file"))


@click.command()
@click.option("--config", default="config.yaml", help="autoscale config", type=click.File())
@click.option("--schema", default="schema.yaml", help="autoscale schema", type=click.File())
def verify(config, schema):
    """Validate config"""
    validate(config, schema)
