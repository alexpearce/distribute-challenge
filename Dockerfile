# Create a Docker image for running Celery workers.
FROM python:3.9

ADD . /app
WORKDIR /app
RUN pip install poetry
RUN poetry install
