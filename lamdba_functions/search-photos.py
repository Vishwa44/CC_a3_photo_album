import logging
import base64
import json
import boto3
import os
import time
import requests
import math
import dateutil.parser
import datetime
import requests


ES_URL = "https://search-photos-xxwie5e2bd4v5nioheu3i77psq.us-east-1.es.amazonaws.com"
ES_USER = 'Master'
ES_PASSWORD = 'Master@123'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

headers = {"Content-Type": "application/json"}
host = ES_URL
region = 'us-east-1'
lex = boto3.client('lexv2-runtime', region_name=region)
import time

def lambda_handler(event, context):
    
    print("EVENT:-  {}".format(json.dumps(event)))
    print(event)
    q1 = event["queryStringParameters"]["q"]
    print(q1)
    
    labels = get_labels(q1)
    print("labels", labels)
    if len(labels) == 0:
        img_paths = {}
    else:
        img_paths = get_image_path(labels)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'imagePaths': img_paths,
            'userQuery': q1,
            'labels': labels,
        }),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        "isBase64Encoded": False
    }
def get_labels(query):
    response = lex.recognize_text(
        botId='64RIDURFWQ',  # Replace with your Lex V2 Bot ID
        botAliasId='TSTALIASID',  # Replace with your Lex V2 Bot Alias ID
        localeId='en_US',  # Replace with your Lex Bot's locale ID
        sessionId='unique_session_id',  # Use a unique session ID for each call
        text=query
    )
    print("lex-response", response)

    labels = []
    if 'slots' not in response['sessionState']['intent']:
        print("No photo collection for query {}".format(query))
    else:
        print("slot: ", response['sessionState']['intent']['slots'])
        slots = response['sessionState']['intent']['slots']
        for key, value in slots.items():
            if value and value.get('value'):
                labels.append(value['value']['interpretedValue'])
    return labels


def get_image_path(labels):
    img_paths = []
    unique_labels = []
    for x in labels:
        if x not in unique_labels:
            unique_labels.append(x)
    labels = unique_labels
    print("inside get photo path", labels)
    for i in labels:
        path = host + '/_search?q=labels:'+i
        print(path)
        response = requests.get(path, headers=headers,
                                auth=(ES_USER, ES_PASSWORD))
        print("response from ES", response)
        dict1 = json.loads(response.text)
        hits_count = dict1['hits']['total']['value']
        print("DICT : ", dict1)
        for k in range(0, hits_count):
            img_obj = dict1["hits"]["hits"]
            img_bucket = dict1["hits"]["hits"][k]["_source"]["bucket"]
            print("img_bucket", img_bucket)
            img_name = dict1["hits"]["hits"][k]["_source"]["objectKey"]
            print("img_name", img_name)
            img_link = 'https://s3.amazonaws.com/' + \
                str(img_bucket) + '/' + str(img_name)
            print(img_link)
            img_paths.append(img_link)
    print(img_paths)
    return img_paths