# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import base64
import boto3
import os
import json
import time

dynamoRecordTTL = 60*60*24*int(os.environ['ITEM_TTL_DAYS'])
tableName = os.environ['TABLE_NAME']

dynamoClient = boto3.client('dynamodb')

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
        response = storeItem(jsonContent["itemId"], jsonContent["userId"], jsonContent["type"])
        print(response)

    return 'Successfully processed {} records.'.format(len(event['Records']))

def storeItem(itemId, userId, type):
    return dynamoClient.update_item(
        ExpressionAttributeNames={
            '#I': 'ItemId',
            '#ttl': 'TTLTime',
        },
        ExpressionAttributeValues={
            ':it': {
                'S': itemId,
            },
            ':ttl': {
                'N': str(int(time.time() + dynamoRecordTTL)),
            },
        },
        Key={
            'UserId': {
                'S': userId,
            },
            'TypeTime': {
                'S': type + "_" + str(int(time.time())),
            },
        },
        ReturnValues='ALL_NEW',
        TableName=tableName,
        UpdateExpression='SET #I = :it, #ttl = :ttl',
    )