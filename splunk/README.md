# pygcplogssplunk
Project based in Python which forwards logs from GCP Project into Splunk

Project reads the logs from a GCP Subscription linked to a pull-based GCP Topic
with Subscription

## Setup

### Locally via Docker
A Dockerfile has been provided to setup the project
```
docker build -t pygcplogssplunk:latest .
```

## Usage

### Via GCP Cloud Shell
```
cd ~/pygcplogssplunk
SPLUNK_URL="http://$SPLUNK_HOST:8088/services/collector" SPLUNK_TOKEN="$SPLUNK_TOKEN" python3 pygcplogssplunk.py
```