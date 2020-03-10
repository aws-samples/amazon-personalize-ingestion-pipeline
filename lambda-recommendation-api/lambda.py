# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import base64
import boto3
import os
import json
import time
from boto3.dynamodb.conditions import Key

campaignArn = os.environ['PERSONALIZE_CAMPAIGN_ARN']
personalizeClient = boto3.client(service_name='personalize-runtime')

def lambda_handler(event, context):
    itemLimit = 10
    itemId = None
    if queryParamPresent("limit", event):
        try:
            queryStringLimit = int(event["queryStringParameters"]["limit"])
            if queryStringLimit > 0 and queryStringLimit < 500:
                itemLimit = queryStringLimit
        except:
            print("Invalid limit, could not parse or not in bounds: ", event["queryStringParameters"]["limit"])
    if queryParamPresent("itemId", event):
        itemId = event["queryStringParameters"]["itemId"]
    # NOTE: We could use multiple solutions here to improve the performance (e.g., for cold starts)
    if 'userId' in event['pathParameters']:
        response = []
        if itemId is None:
            response = personalizeClient.get_recommendations(
                campaignArn=campaignArn,
                userId=event['pathParameters']['userId'],
                numResults=itemLimit,
                #context={
                #    'string': 'string'
                #}
            )
        else:    
            response = personalizeClient.get_recommendations(
                campaignArn=campaignArn,
                itemId=itemId,
                userId=event['pathParameters']['userId'],
                numResults=itemLimit,
                #context={
                #    'string': 'string'
                #}
            )
        responseItems = buildResponse(response['itemList'])
        return {
            "statusCode": 200,
            "body": json.dumps(responseItems)
        }
    else:
        return {"statusCode": 404}
    
def queryParamPresent(paramName, event):
    return "queryStringParameters" in event and event["queryStringParameters"] is not None and paramName in event["queryStringParameters"]

def buildResponse(recommendedItems):
    responseItems = []
    for item in recommendedItems:
        if 'itemId' in item:
            responseItem = {
                "id": item['itemId'],
                # NOTE: Customer can extend this to include additional metadata for the item (image url, title, ...)
            }
            responseItems.append(responseItem)
        else:
            print("Found malformed item, discarding: ", item)
    return responseItems