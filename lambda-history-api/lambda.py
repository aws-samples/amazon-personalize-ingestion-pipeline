# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import base64
import boto3
import os
import json
import time
from boto3.dynamodb.conditions import Key

tableName = os.environ['TABLE_NAME']
dynamoClient = boto3.client('dynamodb')

def lambda_handler(event, context):
    itemLimit = getLimitOrDefault(event, 10)    
    if 'userId' in event['pathParameters']:
        response = getUserImpressionsById(event['pathParameters']['userId'], itemLimit)
        responseItems = []
        for item in response['Items']:
            if 'ItemId' in item:
                viewTime = 0
                try:
                    viewTime = int(item['TypeTime']['S'].split("_")[1])
                except:
                    print("Found malformed item, discarding: ", item)
                    continue
                responseItem = {
                    "id": item['ItemId']['S'],
                    "viewed": viewTime
                }
                responseItems.append(responseItem)
            else:
                print("Found malformed item, discarding: ", item)
        print(response)
        return {
            "statusCode": 200,
            "body": json.dumps(responseItems)
        }
    else:
        return {"statusCode": 404}

def getUserImpressionsById(userId, itemLimit):
    return dynamoClient.query(
            TableName=tableName,
            Limit=itemLimit,
            ConsistentRead=False,
            ScanIndexForward=False, # Necessary since we want most only the X most recent items
            ExpressionAttributeValues={
                ':uid': {
                    'S': userId,
                },
                ':imp': {
                    'S': "impression_",
                },
                ':now': {
                    'N': str(int(time.time())),
                },
            },
            KeyConditionExpression='UserId = :uid AND begins_with(TypeTime, :imp)',
            ProjectionExpression='ItemId,TypeTime',
            FilterExpression= "TTLTime >= :now", # Make sure we're not seeing items that should have been deleted by TTL
        )

def getLimitOrDefault(jsonContent, defaultLimit):
    if "queryStringParameters" in jsonContent and jsonContent["queryStringParameters"] is not None and "limit" in jsonContent["queryStringParameters"]:
        try:
            queryStringLimit = int(jsonContent["queryStringParameters"]["limit"])
            if queryStringLimit > 0 and queryStringLimit < 100:
                return queryStringLimit
        except:
            print("Invalid limit, could not parse or not in bounds: ", jsonContent["queryStringParameters"]["limit"])
    return defaultLimit
