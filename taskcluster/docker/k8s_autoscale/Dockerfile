ARG UV_VERSION
ARG PYTHON_VERSION
FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv
FROM python:$PYTHON_VERSION AS builder

COPY --from=uv /uv /bin
COPY . /app

WORKDIR /app

# %include docker.d
COPY topsrcdir/docker.d/healthcheck /bin/healthcheck
COPY topsrcdir/docker.d/init.sh /app/bin/init.sh

# %include configs
# %include README.rst
# %include pyproject.toml
# %include src
COPY topsrcdir/configs/ /app/configs/
COPY topsrcdir/README.rst /app/
COPY topsrcdir/pyproject.toml /app/
COPY topsrcdir/src/ /app/src/
RUN uv venv
RUN uv pip install .

FROM python:$PYTHON_VERSION

WORKDIR /app
RUN groupadd --gid 10001 app && \
    useradd -g app --uid 10001 --shell /usr/sbin/nologin --create-home --home-dir /app app

COPY --from=builder --chown=app:app /app /app

USER app
CMD ["/app/bin/init.sh"]
