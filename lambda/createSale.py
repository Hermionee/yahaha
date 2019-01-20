import json
import boto3
def lambda_handler(event, context):
    # TODO implement
    print(event)
    dynamo = boto3.client("dynamodb")
    email = dynamo.get_item(
    TableName='UserInfo',
    Key={
        "UserId": {
            'S':event['userID']
            }
    }
    )
    print(email)
    response = dynamo.scan(
    TableName='Products'
    )
    print(response)
    if response['Count']==0:
        Item = {
                    'Owner':{
                      'S': event["userID"] if "userID" in event.keys() else ""
                  },
                  'email':
                      {
                          'S':email['Item']['email']['S']
                      },
                 'ProductName':
                        {
                            'S':event["name"] if "name" in event.keys() else "-"
                        },
                 'Price':
                    {
                        'S':event["price"] if "price" in event.keys() else "-"
                    },
                    'Description':{
                            'S': event['description'] if "description" in event.keys() else "-"
                    },
                    'ProductId':{
                        "S": str(1)
                    }
                    
            }
    else:
        Item ={
            'Owner':{
                      'S': event["userID"] if "userID" in event.keys() else ""
                  },
                  'email':
                      {
                          'S':email['Item']['email']['S']
                      },
                'ProductName':
                    {
                        'S': event["name"] if "name" in event.keys() else "-"
                    },
                'Price':
                {
                    'S': event["price"] if "price" in event.keys() else "-"
                },
                'ProductId':{
                        'S': str(response['Count']+1)
                },
                'Description':{
                    'S': event["description"] if "description" in event.keys() else "-"
                }
        }
    dynamo.put_item(TableName = 'Products', Item = Item, ReturnValues = 'NONE')