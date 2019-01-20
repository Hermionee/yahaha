import json
import boto3
import logging
def lambda_handler(event, context):
    # TODO implement
    client = boto3.client('lex-runtime')
    # if event["message"]["word"].split(";")[1]=="false":
    #     response = client.post_text( botName='GreetingBot',
    #     botAlias='$LATEST',
    #     userId=event["userId"],
    #     inputText=event["message"]["word"].split(";")[0])
    # else:
    #     response = client.post_text( botName='CourseBot',
    #     botAlias='$LATEST',
    #     userId=event["userId"],
    #     inputText=event["message"]["word"].split(";")[0])
        
    # return {"greeting":response["message"]}
    # flavors=["Buffalo Chicken", "Hummus", "Cheese"]
    # if event["word"]=="Hi" or event["word"]=="Hello" or event["word"]=="Hallo":
    #     greeting="Hi, there! How could I help you?"
    # elif event["word"].find("yes")!=-1:
    #     greeting="Which flavors do you like? Buffalo Chicken, Hummus and Cheese? :)"
    
    # elif event["word"] in flavors:
    #     greeting="Gotta, your pizza is on your way! :-p"
    # else:
    #     greeting="Sorry, I don't understand you :-("
    # return {
    #     "greeting": greeting 
    # }
    response = client.post_text( botName='CustomerBot',
         botAlias='$LATEST',
         userId=event["userId"],
         inputText=event["message"]["word"])
    print(response)
    return {"greeting":response["message"]}
