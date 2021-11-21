variable google_project_id {
    type = string
    default = "active-campus-325505"
    description = "Project ID"
}

variable pubsub_topic_name {
  type        = string
  default     = "splunk2"
  description = "Pub/Sub topic to which log messages are written"
}

variable pubsub_subscription_name {
  type        = string
  default     = "splunk2"
  description = "Pub/Sub subscription to which log messages are written"
}

variable project_log_sink_name {
    type = string
    default = "splunk2"
    description = "Name of Log sink to read all logs from the project"
}

variable project_log_sink_description {
    type = string
    default = "Log sink to read all logs from the project"
    description = "Description of the project's log sink"
}

variable project_log_sink_filter { 
    type = string
    # default = "resource.type = gce_instance AND severity >= WARNING"
    default = ""
    description = "Filter to use for the log sink"
}