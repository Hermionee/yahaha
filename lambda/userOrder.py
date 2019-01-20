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
    TableName='Order',
    Key={
        'UserId': {
            'S': event["labels"][0]["q"],
        }
    },
    AttributesToGet=[
        'Date',
        'Name',
        'Price',
        'OrderStatus'
    ]
    )
    print(response)
    if 'Item' not in response.keys():
        return ""
    return {
        "Name": response['Item']['Name']['L'], 
        'Date': response['Item']['Date']['L'],
        'Price':response['Item']['Price']['L'],
        'OrderStatus':response['Item']['OrderStatus']['L'],
        'UserId':event["labels"][0]["q"]
    }