resource "google_pubsub_topic" "pubsub_topic" {
  name = var.pubsub_topic_name
  labels = {
    name = var.pubsub_topic_name
  }
}

# Provide access to the logging sink via the writer identity to publish 
# message to the topic
resource "google_pubsub_topic_iam_binding" "pubsub_topic_binding_for_logsink" {
  project = var.google_project_id
  topic = var.pubsub_topic_name
  role = "roles/pubsub.publisher"
  members = [
    google_logging_project_sink.project_log_sink.writer_identity,
  ]
}

output "pubsub_topic_id" {
  value       = google_pubsub_topic.pubsub_topic.id
  description = "ID of the topic to which logs are written"

}


resource "google_pubsub_subscription" "pubsub_subscription" {
  name  = var.pubsub_subscription_name
  topic = google_pubsub_topic.pubsub_topic.name
  labels = {
    name = var.pubsub_subscription_name
  }
}

resource "google_logging_project_sink" "project_log_sink" {
  name = var.project_log_sink_name
  description = var.project_log_sink_description
  # Can export to pubsub, cloud storage, or bigquery
  destination = "pubsub.googleapis.com/${google_pubsub_topic.pubsub_topic.id}"

  # Log all WARN or higher severity messages relating to instances
  filter = var.project_log_sink_filter

  # Use a unique writer (creates a unique service account used for writing)
  unique_writer_identity = true

  # To disable the log sink, uncomment this
  #disabled = true
}
