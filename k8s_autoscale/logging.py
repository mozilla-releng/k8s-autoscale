import structlog


def get_logger(*args, **kwargs):
    structlog.configure(processors=[structlog.processors.JSONRenderer()])
    return structlog.get_logger(*args, **kwargs)
