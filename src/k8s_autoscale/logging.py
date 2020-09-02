# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import sys

import sentry_sdk
from dockerflow.logging import JsonLogFormatter
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)


def configure_logging(level):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    logging.root.addHandler(handler)
    logging.root.setLevel(level)


def configure_sentry(environment, sentry_dsn):
    logger.info("Enabling Sentry for %s", environment)
    sentry_sdk.init(dsn=sentry_dsn, environment=environment, integrations=[LoggingIntegration()])
