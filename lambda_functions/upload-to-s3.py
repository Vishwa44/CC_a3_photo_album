import json
import base64
import boto3
import string
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print("Something Happened")
    print(event)
    try:
        # Log the entire event for debugging
#         logger.info(f"Received event: {json.dumps(event)}")
        # custom_labels = event.get('headers', {}).get('x-amz-meta-customLabels', '')
        custom_labels = ''
        # print(custom_labels)
        if 'headers' in event:
            if 'x-amz-meta-customlabels' in event['headers']:
                custom_labels = event['headers']['x-amz-meta-customlabels']
                print(custom_labels)
        content_type = 'image/jpeg'
        # Handle different event structures
        if 'body' in event:
            # Check if the body is already base64 encoded
            body = event['body']
            
            # If the body is a string, try to parse it
            if isinstance(body, str):
                try:
                    # Try to parse as JSON first
                    body_dict = json.loads(body)
                    file_content = body_dict.get('image', body)
                    content_type = body_dict.get('file-type', body)
                except json.JSONDecodeError:
                    # If not JSON, assume it's base64 encoded
                    file_content = body
            else:
                # If body is not a string, use it directly
                file_content = body
        elif 'body-json' in event:
            file_content = event['body-json']
        else:
            raise ValueError("No file content found in the event")
        print("Hello");
        # Decode the file content
        try:
            decode_content = base64.b64decode(file_content)
        except Exception as decode_error:
            logger.error(f"Base64 decoding error: {decode_error}")
            raise ValueError("Failed to decode file content")
        
        # Generate unique filename
        pic_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        full_filename = f"{pic_filename}.jpeg"
        
        # Initialize S3 client
        s3 = boto3.client("s3")
        
        # Upload to S3
        s3_upload = s3.put_object(
            Bucket="cc-a3-photos", 
            Key=full_filename, 
            Body=decode_content,
            Metadata={
                'customLabels': custom_labels
            },
            ContentType=content_type
        )
        
        logger.info(f"Successfully uploaded {full_filename} to S3, custom label: {custom_labels}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'The Object is Uploaded successfully!',
                'filename': full_filename,
                'x-amz-meta-customLabels': custom_labels
            }),
            "headers": {
    "Access-Control-Allow-Origin": "*", 
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
  }
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }