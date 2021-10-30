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

