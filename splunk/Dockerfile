FROM alpine:latest
LABEL maintainer=manasmbellani

RUN apk add --update \
    bash \
    python3 \
    py3-pip \
    g++

COPY . /opt/app
# RUN python3 -m pip install -r /opt/app/requirements.txt
WORKDIR /opt/app
