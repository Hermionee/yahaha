import json
import boto3
def lambda_handler(event, context):
    # TODO implement
    dynamo = boto3.client("dynamodb")
    sns = boto3.client("sns")
    products = dynamo.scan(TableName='Products')
    demands = dynamo.scan(TableName='demand')
    print(products)
    print(demands)
    if products['Count']!=0 and demands['Count']!=0:
        for i in range(products['Count']):
            for j in range(demands['Count']):
                book = demands['Items'][j]['book']['S']
                game = demands['Items'][j]['game']['S']
                album = demands['Items'][j]['album']['S']
                drink = demands['Items'][j]['drink']['S']
                
                if book!="-" and (products['Items'][i]['ProductName']['S'].find(demands['Items'][j]['book']['S'])!=-1 or products['Items'][i]['Description']['S'].find(demands['Items'][j]['book']['S'])!=-1):
                    response = sns.publish(
                        PhoneNumber = demands['Items'][j]['phone']['S'],
                        Message="Yahaha you found "+demands['Items'][j]['book']['S']+"! Come online and check it!",
                        # MessageStructure='json',
                        MessageAttributes={
                            'book': {
                                'DataType': 'String',
                                'StringValue':demands['Items'][j]['book']['S']
                            }
                        }
                        )
                    dynamo.delete_item(TableName="demand", Key={
                        "phone":{
                        "S":demands['Items'][j]['phone']['S']
                        }
                    })
                if game!="-" and (products['Items'][i]['ProductName']['S'].find(demands['Items'][j]['game']['S'])!=-1 or products['Items'][i]['Description']['S'].find(demands['Items'][j]['game']['S'])!=-1):
                    response = sns.publish(
                        PhoneNumber = demands['Items'][j]['phone']['S'],
                        Message="Yahaha you found "+demands['Items'][j]['game']['S']+"! Come online and check it!",
                        # MessageStructure='json',
                        MessageAttributes={
                            'book': {
                                'DataType': 'String',
                                'StringValue':demands['Items'][j]['game']['S']
                            }
                        }
                        )
                    dynamo.delete_item(TableName="demand", Key={
                        "phone":{
                        "S":demands['Items'][j]['phone']['S']
                        }
                        })
                if album!="-" and (products['Items'][i]['ProductName']['S'].find(demands['Items'][j]['album']['S'])!=-1 or products['Items'][i]['Description']['S'].find(demands['Items'][j]['album']['S'])!=-1):
                    response = sns.publish(
                        PhoneNumber = demands['Items'][j]['phone']['S'],
                        Message="Yahaha you found "+demands['Items'][j]['album']['S']+"! Come online and check it!",
                        # MessageStructure='json',
                        MessageAttributes={
                            'book': {
                                'DataType': 'String',
                                'StringValue':demands['Items'][j]['album']['S']
                            }
                        }
                        )
                    dynamo.delete_item(TableName="demand", Key={
                        "phone":{
                        "S":demands['Items'][j]['phone']['S']
                        }
                        })
                if drink!="-" and (products['Items'][i]['ProductName']['S'].find(demands['Items'][j]['drink']['S'])!=-1 or products['Items'][i]['Description']['S'].find(demands['Items'][j]['drink']['S'])!=-1):
                    response = sns.publish(
                        PhoneNumber = demands['Items'][j]['phone']['S'],
                        Message="Yahaha you found "+demands['Items'][j]['drink']['S']+"! Come online and check it!",
                        # MessageStructure='json',
                        MessageAttributes={
                            'drink': {
                                'DataType': 'String',
                                'StringValue':demands['Items'][j]['drink']['S']
                            }
                        }
                        )
                    dynamo.delete_item(TableName="demand", Key={
                            "phone":{
                            "S":demands['Items'][j]['phone']['S']
                            }
                        })
                    
