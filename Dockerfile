FROM python:3.7

RUN groupadd --gid 10001 app && \
    useradd -g app --uid 10001 --shell /usr/sbin/nologin --create-home --home-dir /app app

USER app
WORKDIR /app

COPY . /app
# generate /app/version.json according to https://github.com/mozilla-services/Dockerflow/blob/master/docs/version_object.md
RUN ./docker.d/generate_version_json.sh

RUN python -m venv /app
RUN ./bin/pip install -r requirements/base.txt
RUN ./bin/pip install -e .

COPY docker.d/healthcheck /bin/healthcheck
COPY docker.d/init.sh /app/bin/init.sh

CMD ["/app/bin/init.sh"]
