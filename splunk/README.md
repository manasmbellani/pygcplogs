# pygcplogssplunk
Project based in Python which consists of script to forward logs from GCP Project
into Splunk

Project reads the logs via a GCP Subscription linked to a pull-based GCP Topic.

The GCP topic is populated with a log router sink with a specific filter 
configured to receive GCP logs

## Setup

### Generate an Account

### Via UI

Create a service eg. named `pygcplogs` with the following permissions in the 
project: 
* PubSub Admin
* Logging Admin

Download the JSON service account key `pygcplogs-service-account-key.json` and store 
it in folder `/opt/pygcplogs/splunk`

### Deploy Docker container for infrastructure and log forwarding script

#### Via Docker

A Dockerfile has been provided to setup the project including installation of 
pub/sub python libraries:
```
docker build -t pygcplogssplunk:latest .

docker run -v /opt/pygcplogs/splunk:/opt/app -it pygcplogssplunk /bin/bash
```

### Deploy infrastructure such as Pub/Sub Topic, Subscription and Log sink

#### Via Terraform in Docker
```
GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json terraform apply -auto-approve
```

## Usage

### Configure the log reader
Configure the `google_project_id` in `variables.tf` file

### Start the log reader

#### Via Docker
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