import base64
import os
import sys
import uuid
import requests
import urllib
import boto3
import time


def find_labels(client, bucket, key):
    response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        MaxLabels=10,
        MinConfidence=70
    )

    labels = []
    for i in range(len(response['Labels'])):
        labels.append(response['Labels'][i]['Name'])
        print(response['Labels'][i]['Name'])
    return labels
    print(labels)

'''
def find_labels(client, bucket, key):
    Image_string={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        }
    
    print(Image_string)
    #Image_string = Image_string.replace('data:image/jpeg;base64,','')
    
    response = client.detect_labels(
        #Image=base64.b64decode(Image_string),
        Image=Image_string,
        MaxLabels=10,
        MinConfidence=70
    )

    labels = []
    for i in range(len(response['Labels'])):
        labels.append(response['Labels'][i]['Name'])
        print(response['Labels'][i]['Name'])
    return labels
    print(labels.size())
'''
def lambda_handler(event, context):
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    print (bucket)
    print (key)
    '''
    #read image and decode and put it back
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    obj = obj.get()['Body'].read().decode('utf-8')
    obj = base64.b64decode(obj)
    print(obj)
    s3_client = boto3.client('s3')
    s3_client.put_object(Body=obj, Bucket=bucket, Key=key)
    '''
    
    recog = boto3.client('rekognition')
    es = boto3.client('es')
    labels = find_labels(recog, bucket, key)
    host = 'https://vpc-photosdemo-3jss3zxdgmys5l5mi6vkrfhqm4.us-east-1.es.amazonaws.com/'  # The domain with https:// and trailing slash.
    path = 'yahaha2/image/'  # the Elasticsearch API endpoint
    region = 'us-east-1'  # For example, us-west-1

    service = 'es'
    url = host + path + key
    print(labels)
    payload = {
        "objectKey": key,
        "bucket": bucket,
        "createdTimestamp": str(int(round(time.time() * 1000))),
        "labels": labels
    }
    r = requests.put(url, json=payload)  # requests.get, post, and delete have similar syntax
    
    