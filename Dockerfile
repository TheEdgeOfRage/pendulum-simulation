FROM python:3.8-slim

WORKDIR /code
COPY Pipfile Pipfile.lock ./
RUN set -x \
    && pip install pipenv \
    && pipenv install --system --deploy

CMD ["celery", "worker", "--app", "distributed.app", "-E", "-Ofair", "--loglevel=WARN"]

ENV PYTHONPATH=/code \
    PYTHONUNBUFFERED="1" \
    C_FORCE_ROOT="1"

COPY . ./
