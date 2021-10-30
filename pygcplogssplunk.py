#!/usr/bin/env python3
import os
import sys

from google.cloud import pubsub_v1

TOPIC_NAME="splunk"
SUBSCRIPTION_NAME="splunk"


def get_project_id():
    """
    Gets the ID of current project

        Returns:
            str: Current Project's ID
    """
    return os.getenv("GOOGLE_CLOUD_PROJECT")

def check_gcp_subscription_exists(sub_name):
    """
    Checks whether the GCP Pub/Sub subscription exists
    
        Args:
            sub_name(str): Name for the subscription

        Returns:
            bool: True if the GCP Pub/Sub subscription exists
    """
    sub_found = False

    print("[*] Preparing Subscriber client to read subscriptions...")
    subscriber = pubsub_v1.SubscriberClient()
    project_id = get_project_id()
    if project_id:
        project_path = f"projects/{project_id}"
        sub_path = f"projects/{project_id}/subscriptions/{sub_name}"

        print(f"[*] Listing subscriptions in project: {project_path}...")
        for i_sub in subscriber.list_subscriptions(request={"project": project_path}):
            if i_sub.name.lower() == sub_path.lower():
                print(f"[*] Found subscription: {sub_path} in project: {project_path}...")
                sub_found = True
    else:
        print("[-] Project ID for current project not found")

    return sub_found


def check_gcp_topic_exists(topic_name):
    """
    Checks whether the topic exists

        Args:
            topic_name (str): GCP Topic name in GCP Pub/Sub

        Returns:
            bool: True if the GCP topic exists
    """
    topic_found = False

    print("[*] Preparing Publisher client to read topics...")
    project_id = get_project_id()
    if project_id:
        project_path = f"projects/{project_id}"
        topic_path = f"projects/{project_id}/topics/{topic_name}"

        print(f"[*] Listing topics in project: {project_path} via publisher client...")
        publisher = pubsub_v1.PublisherClient()
        for i_topic in publisher.list_topics(request={"project": project_path}):
            if i_topic.name.lower() == topic_path.lower():
                print(f"[*] Found topic: {topic_path} in project: {project_path}...")
                topic_found = True
    else:
        print("[-] Project ID for current project not found")

    return topic_found

def build_subscription(topic_name, sub_name):
    """Builds a subscription to read from specified topic

        Args:
            topic_name(str): Topic to subscribe to
            sub_name(str): Name of the subscription

        Returns:
            bool: True, if subscription created successfully
    """
    subscription_built = False
    project_id = get_project_id()
    if project_id:
        print(f"[*] Building path to topic: {topic_name} via publisher client...")
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)

        print(f"[*] Creating subscription: {sub_name} to topic: {topic_name} via subscription client...")
        with pubsub_v1.SubscriberClient() as subscriber:
            sub_path = subscriber.subscription_path(project_id, sub_name)
            subscriber.create_subscription(request={"name": sub_path, "topic": topic_path})
    else:
        print(f"[-] Project ID could not be read when building subscription: {sub_name}...")
    return subscription_built

def process_messages(sub_name, callback, blocking=True):
    """
    Process messages async from GCP Pub/Sub subscription

        Args:
            sub_name(str): GCP Pub/Sub Subscription name to read messages from
            callback(str): Function to call to process the messages read
            blocking(bool): Whether to block this function when reading messages from subscription
    """
    project_id = get_project_id()
    if project_id:
        print(f"[*] Reading from subscription: {sub_name} with blocking set to {blocking}...")
        with pubsub_v1.SubscriberClient() as subscriber:
            subscription_path = subscriber.subscription_path(project_id, sub_name)
            future = subscriber.subscribe(subscription_path, callback)
            if blocking:
                future.result()
    else:
        print(f"[-] Project ID could not be read when subscribing to subscription: {sub_name}...")

def check_splunk_env_vars_exist():
    """
    Checks whether the Splunk HEC environment vars are defined such as SPLUNK_TOKEN, SPLUNK_URL

        Returns:
            bool: True, if both SPLUNK_URL and SPLUNK_TOKEN are defined. 
    """
    splunk_token = os.getenv("SPLUNK_TOKEN")
    splunk_url = os.getenv("SPLUNK_URL")
    return (not splunk_url || not splunk_token)


def send_to_splunk(message):
    """Sends messages to Splunk HTTP Event Collector (HEC) based on URL, token defined in OS env vars, SPLUNK_URL 
    and SPLUNK_TOKEN

        Args:
            message(PubsubMessage): Pub/Sub Message

    """
    pass


def main():
    splunk_env_vars_defined = check_splunk_env_vars_exist()
    if not splunk_env_vars_defined:
        print(f"[-] Splunk environment variables not defined")
        return 1

    if not check_gcp_topic_exists(TOPIC_NAME):
        print(f"[-] GCP Pub/Sub topic: {TOPIC_NAME} does not exist")
        return 1

    if not check_gcp_subscription_exists(SUBSCRIPTION_NAME):
        if not build_subscription(TOPIC_NAME, SUBSCRIPTION_NAME):
            print(f"[-] Subscription: {SUBSCRIPTION_NAME} not created")
            return 1
    
    
    return 0

if __name__ == "__main__":
    sys.exit(main())