import json
import boto3
from botocore.vendored import requests

def lambda_handler(event, context):
    # TODO implement
    dynamo = boto3.client("dynamodb")
    r = dynamo.get_item(TableName="History", Key={"userId":{"S":event["labels"][0]["q"]}})
    print(r)
    if 'Item' not in r.keys():
        return ""
    count={}
    for j in range(len(r['Item']['Category']['L'])):
        count[r['Item']['Category']['L'][j]["S"]]=1 if r['Item']['Category']['L'][j]["S"] not in count.keys() else count[r['Item']['Category']['L'][j]["S"]]+1
        
    values = list(count.values())
    values.sort()
    biggest = []
    for i in count.keys():
        for j in values:
            if count[i]==j:
                biggest.append(i)
                break
    print(values)
    print(biggest)
    es = boto3.client('es')
    # print(find_labels(client, "photocontainer", "cello.jpg"))
    host = 'https://vpc-photosdemo-3jss3zxdgmys5l5mi6vkrfhqm4.us-east-1.es.amazonaws.com/' # The domain with https:// and trailing slash. 
    path = 'yahaha2/_search?q=' # the Elasticsearch API endpoint
    region = 'us-east-1' # For example, us-west-1
    
    response = []
    results =[]
    for i in range(6):
        service = 'es'
        if len(biggest)<=i:
            res={}
            break
        else:
            url = host + path + biggest[i]
            res = json.loads(requests.get(url).text)
            print(res)
        if "hits" in res.keys():
            if res['hits']['total'] > 0:
                for i in range(res['hits']['total']):
                    if i>=10: break # max is 10
                    results.append("https://s3.amazonaws.com/" + res['hits']['hits'][i]['_source']['bucket']+"/"+ res['hits']['hits'][i]['_source']['objectKey'].replace(" ", "+"))
    content = ""
    for i in range(len(results)):
        content += results[i] + "\n"
    print(content)
    return content
            
            
