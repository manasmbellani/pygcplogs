FROM alpine:latest
LABEL maintainer=manasmbellani

RUN apk add --update \
    bash \
    python3 \
    py3-pip \
    g++ \
    build-base \
    linux-headers \
    python3-dev \
    gcc \
    make \
    terraform

COPY . /opt/app

# Install required deps
RUN python3 -m pip install --upgrade \
    pip \
    requests \
    virtualenv \
    setuptools

# Install google cloud pubsub
RUN mkdir /opt/google-cloud-pubsub && \
    cd /opt/google-cloud-pubsub && \
    python3 -m virtualenv venv && \
    source virtualenv/venv/bin/activate && \
    python3 -m pip install google-cloud-pubsub && \
    deactivate

WORKDIR /opt/app
