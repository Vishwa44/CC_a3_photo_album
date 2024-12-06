import boto3
import base64
import json
import requests

def lambda_handler(event, context):
    print("We are testing invocation")
    s3 = boto3.client('s3')
    rekognition = boto3.client('rekognition')
    
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']

    response = s3.get_object(Bucket=s3_bucket, Key=s3_object_key)
    base64_encoded_image_content = response['Body'].read()

    rekognition_response = rekognition.detect_labels(
        Image= {'Bytes': base64_encoded_image_content},
        MaxLabels=15,  # Maximum labels
        MinConfidence=75  # Minimum confidence for labels
    )

    labels = [label['Name'] for label in rekognition_response['Labels']]
    print('Detected labels:', labels)

    response = s3.head_object(Bucket=s3_bucket, Key=s3_object_key)
    print(response)
    created_timestamp = response['LastModified'].isoformat()

    if 'customlabels' in response['Metadata']:
        custom_labels_string = response['Metadata']['customlabels']
        print(custom_labels_string)
        custom_labels_array = custom_labels_string.split(',')
        labels.extend(custom_labels_array)


    json_object = {
        "objectKey": s3_object_key,
        "bucket": s3_bucket,
        "createdTimestamp": created_timestamp,
        "labels": labels
    }

    auth = ("Master", "Master@123")
    index_name = "photoindex"
    elasticsearch_url = "https://search-photos-xxwie5e2bd4v5nioheu3i77psq.us-east-1.es.amazonaws.com"
    url = f"{elasticsearch_url}/{index_name}/_doc/{s3_object_key}"
    response = requests.post(url, data=json.dumps(json_object), auth=auth, headers={"Content-Type": "application/json"})

    print(response)
    print("Response status code:", response.status_code)
    print("Response headers:", response.headers)
    print("Response content:", response.content.decode('utf-8'))

    return {
        'statusCode': 200,
        'body': labels
    }