#!/usr/bin/env python3
import json
import os
import sys
import time
from datetime import datetime

import requests

from google.cloud import pubsub_v1
from google.protobuf.timestamp_pb2 import Timestamp

TOPIC_NAME = "splunk"
SUBSCRIPTION_NAME = "splunk"
REQUESTS_TIMEOUT = 3
SLEEP_PURGE = 10

def get_project_id():
    """
    Gets the ID of current project

        Returns:
            str: Current Project's ID
    """
    return os.getenv("GOOGLE_CLOUD_PROJECT")

def get_topic_name():
    """
    Get the topic name from environment var TOPIC_NAME, OR a default value
        
        Returns:
            str: Default is defined in TOPIC_NAME constant
    """
    return os.getenv("TOPIC_NAME", default=TOPIC_NAME)

def get_sub_name():
    """
    Get the subscription name from environment var SUB_NAME, OR a default value
        
        Returns:
            str: Default is defined in SUBSCRIPTION_NAME constant
    """
    return os.getenv("SUB_NAME", default=SUBSCRIPTION_NAME)

def get_purge_subscription_flag():
    """Gets the boolean to indicate whether to purge subscription OR not 

        Returns:
            bool: Whether to purge subscriptions or not. Default, False.
    """
    purge_sub_flag = os.getenv("PURGE_SUBSCRIPTION", None)
    if purge_sub_flag is not None:
        return True
    else:
        return False

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

def purge_subscription(sub_name):
    """Purge the specified subscription using seek

    Args:
        sub_name (str): Subscription name

    Returns:
        bool: If the subscription was purged for all messages
    """
    was_sub_purged = False
    project_id = get_project_id()
    if project_id:
        print(f"[*] Purging subscription: {sub_name} via subscription client...")
        with pubsub_v1.SubscriberClient() as subscriber:
            sub_path = subscriber.subscription_path(project_id, sub_name)
            # Get the current timestamp to invoke purge via seek
            timestamp = Timestamp()
            timestamp.GetCurrentTime()
            subscriber.seek(request={"subscription": sub_path, "time": timestamp})
            was_sub_purged = True

    return was_sub_purged

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
                try:
                    future.result()
                except KeyboardInterrupt:
                    print("[*] KeyboardInterrupt encountered... exiting...")
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
    return (splunk_url and splunk_token)


def process_single_message(message):
    """
    Process a GCP Pub/Sub message received asynchronously and ACK it

        Args:
            message: GCP Pub/Sub message
    """
    try:
        #body = message.data.decode(errors='ignore')
        #print(body)
        message_time = datetime.today().ctime()

        print(f"[*] Processing message at time: {message_time}...")
        send_to_splunk(message)
    except Exception as e:
        print(f"[-] Exception processing message. Details: {e.__class__}, {str(e)}")
    finally:
        message.ack()

def send_to_splunk(message, data_error_handling='ignore', ssl_verify=False):
    """Sends messages to Splunk HTTP Event Collector (HEC) based on URL, token defined in OS env vars, SPLUNK_URL 
    and SPLUNK_TOKEN

        Args:
            message(PubsubMessage): GCP Pub/Sub Message
            data_error_handling(str): Ignore errors when decoding data
            ssl_verify(bool): Verify ssl certificate

        Returns:
            bool: True, if message sent successfully to Splunk. False, otherwise.
    """
    message_sent = False
    try:
        splunk_token = os.getenv("SPLUNK_TOKEN")
        splunk_url = os.getenv("SPLUNK_URL")
        headers = {"Authorization": f"Splunk {splunk_token}"}
        event = json.loads(message.data.decode(errors=data_error_handling))
        body = {'event': event}
        
        resp = requests.post(splunk_url, headers=headers, json=body, verify=ssl_verify, allow_redirects=True,
            timeout=REQUESTS_TIMEOUT)
        status_code = resp.status_code
        resp_text = resp.text
        if status_code >= 200 and status_code < 300:
            # data_recvd = resp.data
            # print(data_recvd)
            message_sent = True
        else:
            print(f"[-] Error sending message. Status code: {status_code}, Response: {resp_text}...")
    except Exception as e:
        print(f"[-] Exception sending message to Splunk. Error: {e.__class__}, {str(e)}")
    
    return message_sent

def main():
    splunk_env_vars_defined = check_splunk_env_vars_exist()
    if not splunk_env_vars_defined:
        print(f"[-] Splunk environment variables not defined")
        return 1

    topic_name = get_topic_name()
    print(f"[*] topic_name: {topic_name}")

    sub_name = get_sub_name()
    print(f"[*] sub_name: {sub_name}")

    purge_sub_flag = get_purge_subscription_flag()
    print(f"[*] purge_sub_flag: {purge_sub_flag}")

    if not check_gcp_topic_exists(topic_name):
        print(f"[-] GCP Pub/Sub topic: {topic_name} does not exist")
        return 1

    if not check_gcp_subscription_exists(sub_name):
        if not build_subscription(topic_name, sub_name):
            print(f"[-] Subscription: {sub_name} not created")
            return 1

    if purge_sub_flag:
        if check_gcp_subscription_exists(sub_name):
            if not purge_subscription(sub_name):
                print(f"[-] Subscription: {sub_name} could not be purged")
                return 1

        print(f"[*] Sleeping for {SLEEP_PURGE} seconds after purging...")
        time.sleep(SLEEP_PURGE)
                
    else:
        print(f"[*] Reading from existing subscription: {sub_name}...")
    
    process_messages(sub_name, process_single_message)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())