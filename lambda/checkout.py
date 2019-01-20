import json
import boto3
import time
def lambda_handler(event, context):
    # TODO implement
    dynamo = boto3.client("dynamodb")
    response = dynamo.get_item(
    Key={
        'userId': {
            'S': event['userId'],
        }
    },
    TableName='Cart',
    )
    print(response['Item']['ProductId']['L'])
    # deleted = dynamo.delete_item(
    # Key={
    #     'userId': {
    #         'S': event['userId'],
    #     }
    # },
    # TableName='Cart',
    # )
    sqs = boto3.resource('sqs')
    
    queue = sqs.get_queue_by_name(QueueName='order.fifo')
    print(response)
    for i in range(len(response['Item']['ProductId']['L'])):
        # category=response['Item']['Category']['L'][i]['S']
        description = response['Item']['Description']['L'][i]['S']
        name=response['Item']['ProductName']['L'][i]['S']
        price=response['Item']['Price']['L'][i]['S']
        orderstatus="pending"
        id=response['Item']['ProductId']['L'][i]['S']
        productid = dynamo.scan(
        TableName='Products',
        FilterExpression='ProductId = :id',
        ExpressionAttributeValues={
            ":id": 
                {
                    "S": id
               }
        }
        )
        print(productid)
        owner=productid['Items'][0]["Owner"]['S']
        email=productid['Items'][0]["email"]['S']
        
        sent = queue.send_message(MessageBody = "orders from user " + event['userId'], MessageGroupId = "999",
        MessageAttributes={
                    'Description':{
                      'DataType':'String',
                      'StringValue':description
                    },
                  'Date':{
                      'DataType':'String',
                      'StringValue':time.strftime("%c")
                  },
                  'Name':{
                      'DataType':'String',
                      'StringValue':name
                  },
                  'OrderStatus':{
                      'DataType':'String',
                      'StringValue':orderstatus
                  },
                  'Price':{
                      'DataType':'String',
                      'StringValue':price
                  },
                  'UserId':{
                      'DataType':'String',
                      'StringValue':event['userId']
                  },
                  'Owner':{
                      'DataType':'String',
                      'StringValue':owner
                  },
                  'email':{
                      'DataType':'String',
                      'StringValue':email
                  }
            })
        print(owner)
        print(email)
        print("sent "+ str(i))
        # deleted = dynamo.delete_item(
        # Key={
        #     'ProductId': {
        #     'S': id,
        #     }
        # },
        # TableName='Products',
        # )
        
    deals=dynamo.get_item(TableName = 'UserInfo', Key={
            "UserId":{
                "S": event['userId']
                }
        })
    email=deals['Item']['email']['S']
    dynamo.put_item(TableName = 'UserInfo', Item = {
                "UserId":{
                "S": event['userId']
                },
                "Deals":{
                "S": str(deals['Item']['Deals']['S'])
                },
                "Wishes":{
                "S": str(int(deals['Item']['Wishes']['S'])-len(response['Item']['ProductId']['L']))
                },
                "email":{
                "S": deals['Item']['email']['S']
                }
            }, 
            ReturnValues = 'NONE')
    
    sns = boto3.client("sns")
    response = sns.subscribe(
    TopicArn='arn:aws:sns:us-east-1:267836282592:yahaha',
    Protocol='email',
    Endpoint=email,
    ReturnSubscriptionArn=False
    )
    print(email)
    return {
            "message": "Your order has been placed. Please pay attention to your email and contact the seller for further details!"
    }
