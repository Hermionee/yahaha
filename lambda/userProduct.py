import json

import boto3
from botocore.config import Config
def lambda_handler(event, context):

    config = Config(
        connect_timeout=600, read_timeout=600,
        retries={'max_attempts': 10})
    dynamo = boto3.client('dynamodb', config=config)
    # dynamo.put_item(TableName = 'Order', Item = Item, ReturnValues = 'NONE')
    response = dynamo.scan(
    TableName='Products',
    ExpressionAttributeNames={"#o":"Owner"},
    FilterExpression = '#o=:id',
    ExpressionAttributeValues ={
        ":id":{
            "S":event['labels'][0]['q']
        }
    }
    )
    print(response)
    return response
    
    
        