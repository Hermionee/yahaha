import json
import boto3
from botocore.vendored import requests
from botocore.config import Config
from botocore.exceptions import ClientError
import time
def lambda_handler(event, context):
    # sqs = boto3.resource('sqs')
    queue_url = "https://sqs.us-east-1.amazonaws.com/267836282592/order.fifo"
    # squeue = sqs.Queue(queue_url)
    config = Config(
        connect_timeout=600, read_timeout=600,
        retries={'max_attempts': 10})
    dynamo = boto3.client('dynamodb', config=config)
    # queue = sqs.get_queue_by_name(QueueName='order.fifo')
    sqs = boto3.client("sqs")
    response = sqs.receive_message(QueueUrl=queue_url, MessageAttributeNames=['UserId', 'Name', 'Date', 'Owner', 'email', 'Price'],
        MaxNumberOfMessages=1,
        VisibilityTimeout=30,
        WaitTimeSeconds=20)
        #ReceiveRequestAttemptId='string'
    if 'Messages' not in response.keys():
        return ""
    for m in response['Messages']:
        messages = m['MessageAttributes']
        print(messages)
        receipt_handle = m['ReceiptHandle']
        #Delete received message from queue
        # sqs.delete_message(
        #     QueueUrl=queue_url,
        #     ReceiptHandle=receipt_handle
        # )
        # print(Received and deleted message)
        orders = dynamo.get_item(
        TableName='Order',
        Key={
            "UserId": 
                {
                    "S": messages["UserId"]['StringValue']
               }
        },
        )
        if orders==[]:
            dynamo.update_item(TableName = 'Order', Key={"UserId":{"S":messages["UserId"]['StringValue']}}, 
                ExpressionAttributeNames={"#n":"Name", "#d":"Date"},
                UpdateExpression='SET #n=:n, Price=:price, OrderStatus=:order, #d=:d',
                ExpressionAttributeValues={
                ':n':{
                    "L":[{'S':messages["Name"]['StringValue']}]
                },
                ":price":{
                    "L":[{'S':messages["Price"]['StringValue']}]
                },
                ":order":{
                    "L":[{'S':"received"}]
                },
                ":d":{
                    "L": [{'S': time.strftime("%c")}]
                }
            })
            print("dynamo done")
        else:
            orders['Item']['Name']['L'].append({'S':messages["Name"]['StringValue']})
            orders['Item']['Price']['L'].append({'S':messages["Price"]['StringValue']})
            orders['Item']['OrderStatus']['L'].append({'S': "received"})
            orders['Item']['Date']['L'].append({'S': time.strftime("%c")})
            print(orders)
            
            dynamo.update_item(TableName = 'Order', Key={"UserId":{"S":messages["UserId"]['StringValue']}}, 
                ExpressionAttributeNames={"#n":"Name", "#d":"Date"},
                UpdateExpression='SET #n=:n, Price=:price, OrderStatus=:order, #d=:d',
                ExpressionAttributeValues={
                    ':n':{
                        "L":orders['Item']['Name']['L']
                    },
                    ":price":{
                        "L":orders['Item']['Price']['L']
                    },
                    ":order":{
                        "L":orders['Item']['OrderStatus']['L']
                    },
                    ":d":{
                        "L": orders['Item']['Date']['L']
                    }
                })
            print("dynamo done")
        
        deals=dynamo.get_item(TableName = 'UserInfo', Key={
            "UserId":{
                "S": messages["UserId"]['StringValue']
                }
        })
        dynamo.update_item(TableName = 'UserInfo', Key = {
                "UserId":{
                "S": messages["UserId"]['StringValue']
                }
                },
                UpdateExpression='SET Deals=:d, Wishes=:w',
                ExpressionAttributeValues={
                ":d":{
                "S": str(int(deals['Item']['Deals']['S'])+1)
                },
                ":w":{
                "S": deals['Item']['Wishes']['S']
                }
            }
           )
        # Replace sender@example.com with your "From" address.
        # This address must be verified with Amazon SES.
        SENDER = "YAHAHA <dh2914@columbia.edu>"
        
        # Replace recipient@example.com with a "To" address. If your account 
        # is still in the sandbox, this address must be verified.
        response = dynamo.get_item(
               TableName = 'UserInfo', 
               Key={
                   'UserId': 
                    {'S':messages["UserId"]['StringValue']}
                }
            )
        RECIPIENT = "dh2914@columbia.edu"
        # RECIPIENT = "neo425631120@gmail.com"
        print(RECIPIENT)
        
        AWS_REGION = "us-east-1"
        print(messages)
        SUBJECT = "YAHAHA - Your order has been confirmed."
        
        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = ("Hi friend, \r\n"
                     "This email was sent from "
                     "TEAM YAHAHA (COLUMBIA)."
                    )
                    
        # The HTML body of the email.
        BODY_HTML = "<html><head></head><body><h1>YAHAHA CONFIRMATION</h1><p>You are buying " + messages["Name"]['StringValue'] + " at " + messages["Price"]['StringValue'] + " on " + messages["Date"]['StringValue'] + ".\n Please contact the seller" + messages["Owner"]['StringValue'] + " for futher information and pickup details. Your seller email is " +messages["email"]['StringValue'] + ".</p><p>This email was sent from <a href='https://s3.amazonaws.com/finalproject-yahaha/Final+project/logindex.html'>YAHAHA</a> using the <a href='https://aws.amazon.com/sdk-for-python/'>AWS SDK for Python (Boto)</a>.</p></body></html>."

        # The character encoding for the email.
        CHARSET = "UTF-8"
        
        # Create a new SES resource and specify a region.
        client = boto3.client('ses',region_name=AWS_REGION)
        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
        
            