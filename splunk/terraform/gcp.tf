terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.1.0"
    }
  }
}

provider "google" {
  project     = "active-campus-325505"
  region      = "us-central1"
}