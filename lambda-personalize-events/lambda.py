# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import base64
import boto3
import os
import json
import time
import uuid

trackingId = os.environ['TRACKING_ID']

personalize_events = boto3.client(service_name='personalize-events')

def lambda_handler(event, context):
    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record['kinesis']['data'])
        jsonContent = {}
        try:
            jsonContent = json.loads(payload)
        except:
            print("Could not parse: " + payload)
            continue

        sessionId = getSessionIdOrRandom(jsonContent)

        personalize_events.put_events(
            trackingId = trackingId,
            userId= jsonContent["userId"],
            sessionId = sessionId,
            eventList = [{
                'sentAt': jsonContent["time"],
                'eventType': jsonContent["type"],
                'properties': "{\"itemId\": \"" + jsonContent['itemId'] + "\"}"
                }]
        )

    return 'Successfully processed {} records.'.format(len(event['Records']))

def getSessionIdOrRandom(jsonContent):
    if "sessionId" in jsonContent:
        return jsonContent["sessionId"]
    else:
        return str(uuid.uuid4())