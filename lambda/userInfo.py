import json

import boto3
from botocore.config import Config
def lambda_handler(event, context):

    config = Config(
        connect_timeout=600, read_timeout=600,
        retries={'max_attempts': 10})
    dynamo = boto3.client('dynamodb', config=config)
    # dynamo.put_item(TableName = 'Order', Item = Item, ReturnValues = 'NONE')
    response = dynamo.get_item(
    TableName='UserInfo',
    Key={
        'UserId': {
            'S': event["labels"][0]["q"],
        }
    },
    AttributesToGet=[
        'Deals',
        'Wishes'
    ]
    )
    if 'Item' not in response.keys():
        return {
            "Deals": "0",
            "Wishes": "0",
            "UserId": event["labels"][0]["q"]
        }
    else:
        return {
            "Deals": response["Item"]["Deals"]['S'],
            "Wishes": response["Item"]["Wishes"]['S'],
            "UserId": event["labels"][0]["q"]
        }