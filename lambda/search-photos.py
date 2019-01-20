
from botocore.vendored import requests
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import json
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_dining_config(key):
    Keyword = ['ball', 'instrument', 'mountain', 'book', 'nebula', 'building', 'person','sports']
    if key is not None and key.lower() not in Keyword:
        return build_validation_result(False,
                                    'key',
                                    'I dont\'t know about {}, would you like to see a different thing?'
                                    'You can try "chairs" or "stones"'.format(key))
    return build_validation_result(True, None, None)

""" --- Main handler --- """

def lambda_handler(event, context):
    print(event)
    es = boto3.client('es')
    # print(find_labels(client, "photocontainer", "cello.jpg"))
    host = 'https://vpc-photosdemo-3jss3zxdgmys5l5mi6vkrfhqm4.us-east-1.es.amazonaws.com/' # The domain with https:// and trailing slash. 
    path = 'yahaha2/_search?q=' # the Elasticsearch API endpoint
    region = 'us-east-1' # For example, us-west-1
    
    # logger.debug('dispatch userId={}, intentName={}'.format(event['userId'], event['currentIntent']['name']))
    
    intent_name = event['currentIntent']['name']
    # Dispatch to your bot's intent handlers
    if intent_name == 'SearchIntent':
        keyword = get_slots(event)["keyword"] if get_slots(event)["keyword"] is not None else ""
        otherkeyword = get_slots(event)["otherkeyword"] if get_slots(event)["otherkeyword"] is not None else ""
        slots = get_slots(event)
        # validation_result_keyword = validate_dining_config(keyword)
        # validation_result_otherkeyword = validate_dining_config(otherkeyword)
        # valid_photo={}
        # valid_photo['keyword']= keyword
        # valid_photo['otherkeyword']=otherkeyword
        # if not validation_result_keyword['isValid']:
        #     slots[validation_result_keyword['violatedSlot']] = None
        #     valid_photo['keyword'] = None

        # if not validation_result_otherkeyword['isValid']:
        #     slots[validation_result_otherkeyword['violatedSlot']] = None
        #     valid_photo['otherkeyword'] = None
            
        # if not validation_result_keyword['isValid'] and not validation_result_otherkeyword['isValid']:
        #     Message = "I haven't stored " +keyword +" and " +otherkeyword +" type of photos, would you like to see a different thing?"
        #     response_fail = {
        #     # 'sessionAttributes': event['sessionAttributes'],
        #       'dialogAction': {
        #           'type': 'Close',
        #           'fulfillmentState': 'Fulfilled',
        #           'message':{
        #               "contentType": "PlainText",
        #               "content": Message
        #           }
        #       }
        #     }
        #     return response_fail

        # if valid_photo['keyword'] is None and valid_photo['otherkeyword'] is not None:
        #     keyword =""
        #     response_content = " the photos of " + otherkeyword + " are on the way!"
            
        # elif valid_photo['otherkeyword'] is None and valid_photo['keyword'] is not None:
        #     otherkeyword = ""
        #     response_content = " the photos of " + keyword + " are on the way!"
        # elif valid_photo['otherkeyword'] is None and valid_photo['keyword'] is None:
        #     otherkeyword = ""
        #     keyword = ""
        # else:
        #     response_content = "the photos of "+ keyword +" and " + otherkeyword +" are on the way!"
    
    results =[]
    service = 'es'
    url = host + path + keyword
    res = json.loads(requests.get(url).text)
    if "hits" in res.keys():
        if res['hits']['total'] > 0:
            for i in range(res['hits']['total']):
                if i>=10: break # max is 10
                results.append("https://s3.amazonaws.com/" + res['hits']['hits'][i]['_source']['bucket']+"/"+ res['hits']['hits'][i]['_source']['objectKey'].replace(" ", "+"))
            dynamo=boto3.client("dynamodb")
            re = dynamo.get_item(TableName="History", Key={
                "userId":{
                    "S":event["userId"]
                }
            })
            print(re)
            if 'Item' not in re.keys():
                dynamo.put_item(TableName="History", Item={
                   "userId":{
                    "S":event["userId"]
                },
                "Category":{
                    "L":[{
                        "S":keyword
                        }]
                }
                })
            else:
                dynamo.update_item(TableName="History", 
                    UpdateExpression='SET Category = list_append(Category, :c)',
                    Key={
                    "userId":{
                        "S":event["userId"]
                        }
                    },
                    ExpressionAttributeValues={
                    ":c":{
                        "L":[{
                            "S":keyword
                            }]
                        }
                 })
        
    url = host + path + otherkeyword
    res = json.loads(requests.get(url).text)
    if "hits" in res.keys():
        if res['hits']['total'] > 0:
            for i in range(res['hits']['total']):
                print(i)
                if i>=10: break # max is 10
                if "https://s3.amazonaws.com/" + res['hits']['hits'][i]['_source']['bucket']+"/"+ res['hits']['hits'][i]['_source']['objectKey'].replace(" ", "_") not in results:
                    results.append("https://s3.amazonaws.com/" + res['hits']['hits'][i]['_source']['bucket']+"/"+ res['hits']['hits'][i]['_source']['objectKey'].replace(" ", "+"))
            dynamo=boto3.client("dynamodb")
            re = dynamo.get_item(TableName="History", Key={
                "userId":{
                    "S":event["userId"]
                }
            })
            print(re)
            if 'Item' not in re.keys():
                dynamo.put_item(TableName="History", Item={
                   "userId":{
                    "S":event["userId"]
                },
                "Category":{
                    "L":[{
                        "S":otherkeyword
                        }]
                }
                })
            else:
                dynamo.update_item(TableName="History", 
                    UpdateExpression='SET Category = list_append(Category, :c)',
                    Key={
                    "userId":{
                        "S":event["userId"]
                        }
                    },
                    ExpressionAttributeValues={
                    ":c":{
                        "L":[{
                            "S":otherkeyword
                            }]
                        }
                 })
    
    content = ""
    if len(results)==0:
        response = {
              'dialogAction': {
                  'type': 'Close',
                  'fulfillmentState': 'Fulfilled',
                  'message':{
                       "contentType": "PlainText",
                       "content": "Ooops, Photo not found >_<"
                  }
              }
    }
    else:
        for i in range(len(results)):
            content += results[i] + "\n"
        response = {
            'dialogAction': {
                      'type': 'Close',
                      'fulfillmentState': 'Fulfilled',
                      'message':{
                           "contentType": "PlainText",
                           "content": content
                      }
                  }
        }
    print(response)
    return response