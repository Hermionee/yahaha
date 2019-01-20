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
    TableName='Cart',
    Key={
        'userId': {
            'S': event["labels"][0]["q"]
        }
    },
    AttributesToGet=[
        'ProductId',
        'Description',
        'Price',
        'ProductName'
    ]
    )
    if 'Item' not in response.keys():
        return {
        "ProductId": "" ,
        'Price': "", 
        'Description': "", 
        'ProductName': ""
        }
    else:
        # dynamo = boto3.client("dynamodb")
        
        # response = dynamo.put_item(TableName="Cart", Item={
        #     "userId":{
        #         "S":event["labels"][0]["q"]
        #     },
        #     "ProductId": {
        #         "L":response['Item']['ProductId']['L']
        #         },
        #     'Price': {
        #         "L":response['Item']['Price']['L']
        #         },
        #     'Description':{
        #         "L":response['Item']['Description']['L']
        #         },
        #     'ProductName': {
        #         "L":response['Item']['ProductName']['L']
        #         }
        # })
        return {
            "ProductId": response['Item']['ProductId']['L'], 
            'Price': response['Item']['Price']['L'], 
            'Description': response['Item']['Description']['L'], 
            'ProductName': response['Item']['ProductName']['L']
        }