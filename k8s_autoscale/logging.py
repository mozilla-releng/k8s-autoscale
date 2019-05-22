import structlog


def get_logger(*args, **kwargs):
    return structlog.get_logger(*args, **kwargs)
