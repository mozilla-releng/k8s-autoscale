ARG PYTHON_VERSION
FROM python:$PYTHON_VERSION

RUN groupadd --gid 10001 app && \
    useradd -g app --uid 10001 --shell /usr/sbin/nologin --create-home --home-dir /app app

COPY . /app

WORKDIR /app

# %include version.txt
COPY topsrcdir/version.txt /app/version.txt

# %include docker.d
COPY topsrcdir/docker.d/healthcheck /bin/healthcheck
COPY topsrcdir/docker.d/init.sh /app/bin/init.sh

# %include configs
# %include requirements
# %include MANIFEST.in
# %include README.rst
# %include pyproject.toml
# %include setup.py
# %include src
COPY topsrcdir/configs/ /app/configs/
COPY topsrcdir/requirements/ /app/requirements/
COPY topsrcdir/MANIFEST.in /app/
COPY topsrcdir/README.rst /app/
COPY topsrcdir/pyproject.toml /app/
COPY topsrcdir/setup.py /app/
COPY topsrcdir/src/ /app/src/
RUN python -m venv /app
RUN ./bin/pip install -r /app/requirements/base.txt
RUN ./bin/pip install -e .

RUN chown -R app:app /app

# %include-run-task

VOLUME /builds/worker/checkouts
VOLUME /builds/worker/.cache

USER app
CMD ["/app/bin/init.sh"]
