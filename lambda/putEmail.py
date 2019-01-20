import json
import boto3
def lambda_handler(event, context):
    # TODO implement
    dynamo = boto3.client("dynamodb")
    print(event)
    Item = {
                'UserId':{
                  'S': event['userId']
              },
             'email':{
                 'S':event["email"]
             },
             'Wishes':{
                 'S':"0"
             },
             'Deals':{
                 'S':"0"
             },
             'Rating':{
                 'S':"0"
             }
        }
    print(Item)
    dynamo.put_item(TableName = 'UserInfo', Item = Item, ReturnValues = 'NONE')
    print("dynamo done")
