# pygcplogssumologic
Project based in Python which consists of script to forward logs from GCP Project
into Sumologic

Project reads the logs via a GCP Subscription linked to a pull-based GCP Topic.

The GCP topic is populated with a log router sink with a specific filter 
configured to receive GCP logs

## Setup

### Generate an Account

#### Via UI

Create a service account eg. named `pygcplogs` with the following permissions in the 
project: 
* Pub/Sub Admin - Ability to create pub/sub topic, subscription and assign the 
log router sink
* Logging Admin - Ability to create log router sink

Download the JSON service account key `pygcplogs-service-account-key.json` and store 
it in folder `/opt/pygcplogs/sumologic`

### Enable the Services

#### Via UI

Visit `Pub/Sub` and `Logging` > `Logs Storage` in the GCP project via GCP Console 
and enable the relevant services for the project.

### Deploy Docker container for infrastructure and log forwarding script

#### Via Docker

A Dockerfile has been provided to setup the project including installation of 
pub/sub python libraries:
```
docker build -t pygcplogssumologic:latest .

docker run -v /opt/pygcplogs/sumologic:/opt/app -it pygcplogssumologic /bin/bash
```

If the container is stopped, then the following code starts the container:
```
container_id=$(docker container ls -a | grep -i pygcplogssumologic | cut -d" " -f1)
docker start $container_id
docker exec -it $container_id /bin/bash
```

### Deploy infrastructure such as Pub/Sub Topic, Subscription and Log sink

#### Via Terraform in Docker
Configure the `google_project_id` in `variables.tf` file if we wish to change the
name or description of pub/sub topics, subscription or logging sink

Then execute the command below to create the pub/sub topics:
```
cd /opt/app/terraform
PROJECT_ID="..."
GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json \
TF_VAR_google_project_id="$PROJECT_ID" \
terraform apply -auto-approve
```

## Usage

### Start the log forwarder

#### Via Docker
First define the Sumologic Collector URL and project ID to read the logs from: 
```
SUMOLOGIC_URL="...."   
PROJECT_ID="..."
```

Start the log forwarder and purge previous messages via the `PURGE_SUBSCRIPTION` env var:
```
cd /opt/google-cloud-pubsub
source venv/bin/activate

GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
SUMOLOGIC_URL="$SUMOLOGIC_URL" \
GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json \
PURGE_SUBSCRIPTION=1 \
python3 /opt/app/pygcplogs.py
```

#### Via GCP Cloud Shell
This is similar to launching from docker container and requires the same env 
vars to be set as Docker container above
```
cd ~/pygcplogssumologic

gcloud config set project "$PROJECT_ID"

GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
SUMOLOGIC_URL="$SUMOLOGIC_URL" \
GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json \
python3 pygcplogs.py
```

### Remove infrastructure such as Pub/Sub Topic, Subscription and Log sink

#### Via Terraform in Docker
Execute the command below to destroy the pub/sub topics:
```
cd /opt/app/terraform
PROJECT_ID="..."
GOOGLE_APPLICATION_CREDENTIALS=/opt/app/pygcplogs-service-account-key.json \
TF_VAR_google_project_id="$PROJECT_ID" \
terraform destroy -auto-approve
```