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


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


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


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_asking_config(intent_request, book, album, drink, game):
    if book is not None:
        notnone = book 
    if album is not None:
        notnone = album
    if drink is not None:
        notnone = drink
    if game is not None:
        notnone = game
    
    intent_request['sessionAttributes']=intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    dynamo = boto3.client("dynamodb")
    response = dynamo.scan(TableName='Products')
    if response['Count']!=0:
        findifnameexist = []
        findifdiscexist = []
        for i in range(response['Count']):
            print(response['Items'][i])
            findifnameexist.append(response['Items'][i]['ProductName']['S'].find(notnone))
            findifdiscexist.append(response['Items'][i]['Description']['S'].find(notnone))
        print(findifnameexist)
        print(findifdiscexist)
        if book is not None and (0 not in findifnameexist and 0 not in findifdiscexist):
            intent_request['sessionAttributes']['book']=book
            return build_validation_result(False,
                                   'book',
                                   'I am sorry that we dont\'t have {}, but we will publish to help you find it! We will inform you as long as there are similar books available! Could you tell us your phone number?'.format(book))
        if album is not None and (0 not in findifnameexist and 0 not in findifdiscexist):
            intent_request['sessionAttributes']['album']=album
            return build_validation_result(False,
                                   'album',
                                   'I am sorry that we dont\'t have {}, but we will publish to help you find it! We will inform you as long as it\'s available! Could you tell us your phone number?'.format(album))
        if drink is not None and (0 not in findifnameexist and 0 not in findifdiscexist):
            intent_request['sessionAttributes']['drink']=drink
            return build_validation_result(False,
                                   'drink',
                                   'I am sorry that {} are sold out, but we will advocate people to sell it more! Next time seize your chance! Could you tell us your phone number?'.format(drink))
        if game is not None and (0 not in findifnameexist and 0 not in findifdiscexist):
            intent_request['sessionAttributes']['game']=game
            return build_validation_result(False,
                                   'game',
                                   'It seems {} are really hot, we will keeping looking for information for you and inform you as long as it\'s available! Could you tell us your phone number?'.format(game))
    else:
        return build_validation_result(False,
                                       'phone',
                                       'Buddy bad luck. We are out of everything now. But we will refill our repository soon! Try some luck next time! Could you tell us your phone number? We will message you whenever there is somthing posted!')
    
    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """

def say_hi(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Hi there! How can I help you?'})

def say_bye(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Bye, have a good day :p'})
                  
def asking(intent_request):
    book = get_slots(intent_request)["book"]
    album = get_slots(intent_request)["album"]
    drink = get_slots(intent_request)["drink"]
    game = get_slots(intent_request)["game"]
    phone = get_slots(intent_request)["phone"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)
        
        if phone is None:
            if book is None and album is None and drink is None and game is None:
                return elicit_slot(intent_request['sessionAttributes'],
                                       intent_request['currentIntent']['name'],
                                       slots,
                                       'game',
                                       {'contentType': 'PlainText', 'content': 'sorry can you please change another word? I don\'t recognize that'})
            validation_result = validate_asking_config(intent_request, book, album, drink, game)
            if not validation_result['isValid']:
                slots[validation_result['violatedSlot']] = None
                output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
                return elicit_slot(output_session_attributes,
                                   intent_request['currentIntent']['name'],
                                   slots,
                                   validation_result['violatedSlot'],
                                   validation_result['message'])
        else:
            dynamo = boto3.client("dynamodb")
            if 'book' in intent_request['sessionAttributes'].keys():
                book = intent_request['sessionAttributes']['book']
            else:
                book = "-"
            if 'album' in intent_request['sessionAttributes'].keys():
                album = intent_request['sessionAttributes']['album']
            else:
                album = "-"
            if 'game' in intent_request['sessionAttributes'].keys():
                game = intent_request['sessionAttributes']['game']
            else:
                game = "-"
            if 'drink' in intent_request['sessionAttributes'].keys():
                drink = intent_request['sessionAttributes']['drink']
            else:
                drink = "-"
            response = dynamo.put_item(TableName='demand', Item={
                "phone":{
                    'S':phone
                    },
                "book":{
                    'S':book
                    },
                "album":{
                    'S':album
                    },
                "game":{
                    'S':game
                    },
                "drink":{
                    'S':drink
                    }
            })
            return {
                # 'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled',
                    'message':{
                         "contentType": "PlainText",
                         "content": "Gotcha! Yahaha you wil find it!"
                    }
                }
            }
    response = {
        # 'sessionAttributes': event['sessionAttributes'],
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message':{
                 "contentType": "PlainText",
                 "content": "Yahaha you found it! Just search it, someone is selling!"
            }
        }
    }

    return response

""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return say_hi(intent_request)
    elif intent_name == 'ThankyouIntent':
        return say_bye(intent_request)
    elif intent_name == 'ReturnIntent':
        return asking(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
