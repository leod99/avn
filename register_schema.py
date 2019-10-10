#!/usr/bin/python
import os
import sys
import requests


SCHEMA_REGISTRY_URL = 'https://avnadmin:passwordi2s@kafka-282e881e-chrdeng9-e577.aivencloud.com:16123'
KAFKA_CONNECT_URL = 'https://avnadmin:password7mx@kafka-282e881e-chrdeng9-e577.aivencloud.com:16118'
TOPIC = 'metrics'
# value schema file
SCHEMA_FILE = 'metrics_schema.json'
# sink connector config file
CONNECTOR_CONFIG_FILE = 'sink_config.json'


def register_schema(schema_file, schema_type):
    print("pwd: %s" % os.getcwd())
    print("Schema Registry URL: " + SCHEMA_REGISTRY_URL)
    print("Topic: " + TOPIC)
    print("Schema file: %s\n" % schema_file)

    with open(schema_file, 'r') as content_file:
        schema = content_file.read()

    payload = "{ \"schema\": \"" \
              + schema.replace("\"", "\\\"").replace("\t", "").replace("\n", "") \
              + "\" }"

    url = SCHEMA_REGISTRY_URL + "/subjects/" + TOPIC + "-"+ schema_type+"/versions"
    headers = {"Content-Type": "application/vnd.schemaregistry.v1+json"}

    r = requests.post(url, headers=headers, data=payload)
    print("Register schema return code: %s" % r.status_code)
    if requests.codes.ok <= r.status_code < 300:
        print("Register schema Success")
    else:
        r.raise_for_status()


def add_connector(config_file):

    with open(config_file, 'r') as content_file:
        config = content_file.read()

    payload = config.replace("\t", "").replace("\n", "")

    url = KAFKA_CONNECT_URL + "/connectors"
    headers = {"Content-Type": "application/json"}

    r = requests.post(url, headers=headers, data=payload)
    print("Add connector return code: %s" % r.status_code)
    if requests.codes.ok <= r.status_code < 300:
        print("Add connector Success")
    else:
        r.raise_for_status()


def main():
    schema_file = os.getcwd() + "/json/" + SCHEMA_FILE
    register_schema(schema_file, "value")

    connector_config_file = os.getcwd() + "/json/" + CONNECTOR_CONFIG_FILE
    add_connector(connector_config_file)


if __name__ == "__main__":
    main()
