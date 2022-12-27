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
* PubSub Admin - Ability to create pub/sub topic, subscription and assign the 
log router sink
* Logging Admin - Ability to create log router sink

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
Configure the `google_project_id` in `variables.tf` file if we wish to change the
name or description of pub/sub topics, subscription or logging sink

Then execute the command below to create the pub/sub topics
```
cd /opt/app/terraform

# Invoke terraform init the first time...
terraform init

# Create the infrastructure 
GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json \
TF_VAR_google_project_id="active-campus-325505" \
terraform apply -auto-approve
```

## Usage

### Configure a HTTP Event Collector in Splunk

#### Via UI
Login to Splunk UI > Settings > Data > Data Inputs > HTTP Event Collector

Select `New Token` > enter Name `splunk` > Provide valid description > Next

Select appropriate `Source Type` eg. `_json` > select `Index` e.g. `main` > Review

Review the info > Select `Done`

Visit `Global Settings` > `Enabled` All Tokens > Select `Enable SSL` > 
> Enable SSL > Select HTTP Port Number e.g. `8088` > `Save`

### Start the log forwarder

#### Via Docker
First define the Splunk token, IP and project ID to read the logs from: 
```
SPLUNK_IP="...."
SPLUNK_TOKEN="...."
PROJECT_ID="..."
```

Start the log forwarder:
```
cd /opt/google-cloud-pubsub
source venv/bin/activate

GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
SPLUNK_URL="https://$SPLUNK_IP:8088/services/collector" \
SPLUNK_TOKEN="$SPLUNK_TOKEN" \
GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json \
python3 /opt/app/pygcplogs.py
```

#### Via GCP Cloud Shell
This is similar to launching from docker container and requires the same env 
vars to be set as Docker container above
```
cd ~/pygcplogssplunk

gcloud config set project "$PROJECT_ID"

SPLUNK_URL="https://$SPLUNK_IP:8088/services/collector" \
SPLUNK_TOKEN="$SPLUNK_TOKEN" \
GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json \
python3 pygcplogssplunk.py
```