import json
import boto3
def lambda_handler(event, context):
    # TODO implement
    print(event)
    dynamo = boto3.client("dynamodb")
    response = dynamo.scan(
    TableName='Cart',
    FilterExpression='userId = :user',
    ExpressionAttributeValues={
        ":user": 
            {
                "S": event['userId']
           }
    },
    )
    if response['Count']==0:
        Item = {
                    'userId':{
                      'S': event["userId"] if "userId" in event.keys() else ""
                  },
                 'ProductName':
                        {
                            'L': [{'S':event["name"] if "name" in event.keys() else "-"}]
                        },
                 'Price':
                    {
                        'L': [{'S':event["price"] if "price" in event.keys() else "-"}]
                    },
                    'Description':{
                            'L': [{'S':event['description'] if "description" in event.keys() else "-"}]
                    },
                    'ProductId':{
                        "L": [{'S':str(1)}]
                    }
                    
            }
    else:
        response['Items'][0]['ProductName']['L'].append({'S': event["name"] if "name" in event.keys() else "-"})
        response['Items'][0]['Price']['L'].append({'S': event["price"] if "price" in event.keys() else "-"})
        response['Items'][0]['ProductId']['L'].append({'S': str(len(response['Items'][0]['ProductId'])+1)})
        response['Items'][0]['Description']['L'].append({'S': event["description"] if "description" in event.keys() else "-"})
        Item ={
            'userId':{
                      'S': event["userId"] if "userId" in event.keys() else ""
                  },
            'ProductName':
                    {
                        'L': response['Items'][0]['ProductName']['L']
                    },
             'Price':
                {
                    'L': response['Items'][0]['Price']['L']
                },
                'ProductId':{
                        'L': response['Items'][0]['ProductId']['L']
                },
                'Description':{
                    'L': response['Items'][0]['Description']['L']
                }
        }
    dynamo.put_item(TableName = 'Cart', Item = Item, ReturnValues = 'NONE')
    deals=dynamo.get_item(TableName = 'UserInfo', Key={
            "UserId":{
                "S": event["userId"]
                }
        })
    dynamo.put_item(TableName = 'UserInfo', Item = {
                "UserId":{
                "S": event["userId"]
                },
                "Deals":{
                "S": deals['Item']['Deals']['S']
                },
                "Wishes":{
                "S": str(int(deals['Item']['Wishes']['S'])+1)
                },
                "email":{
                "S": deals['Item']['email']['S']
                }
            }
            , ReturnValues = 'NONE')