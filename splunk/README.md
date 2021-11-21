# pygcplogssplunk
Project based in Python which forwards logs from GCP Project into Splunk

Project reads the logs from a GCP Subscription linked to a pull-based GCP Topic
with Subscription

## Setup

### Locally via Docker
A Dockerfile has been provided to setup the project
```
docker build -t pygcplogssplunk:latest .

docker run -v /opt/pygcplogs/splunk:/opt/app -it pygcplogssplunk /bin/bash
```

## Usage

### In Dockerfile

#### Deploy the infrastructure

```
cd /opt/app/splunk/terraform

GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json terraform apply
```

#### Start the log reader
```
cd /opt/google-cloud-pubsub
source venv/bin/activate

GOOGLE_CLOUD_PROJECT="active-campus-325505" SPLUNK_URL="http://54.153.162.91:8088/services/collector" SPLUNK_TOKEN="$SPLUNK_TOKEN" GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json python3 /opt/app/pygcplogs.py
```

### Via GCP Cloud Shell
```
cd ~/pygcplogssplunk

SPLUNK_URL="http://54.153.162.91:8088/services/collector" SPLUNK_TOKEN="$SPLUNK_TOKEN" GOOGLE_CLOUD_PROJECT="$GOOGLE_CLOUD_PROJECT_ID" GOOGLE_APPLICATION_CREDENTIALS="$GOOGLE_APPLICATION_CREDENTIALS_FILE" python3 pygcplogssplunk.py
```