import json
import boto3
import datetime
import urllib3

# Elasticsearch config
ES_CONFIG = {
    "url": "https://search-yelp-restaurants-es-coi3ozmqyi2g5vr624aing4dja.us-east-1.es.amazonaws.com/",
    "index": "photos",
    "type": "photo",
    "master-username": "chatbot-es-root",
    "master-password": "CCBD-es-123456"
}

def store_in_es(bucket, file, labels):
    """
    Make an Elasticsearch query
    """
    http = urllib3.PoolManager()
    url = "%s%s/%s/" % (ES_CONFIG["url"], ES_CONFIG["index"], ES_CONFIG["type"])
    headers = urllib3.make_headers(basic_auth='%s:%s' % (ES_CONFIG["master-username"], ES_CONFIG["master-password"]))
    print(headers)
    headers.update({
        'Content-Type': 'application/json',
        "Accept": "application/json"
    })
    payload = {
        "object_key": file,
        "bucket": bucket,
        "createdTimestamp": str(datetime.datetime.now().strftime("%Y-%m-%d"'T'"%H:%M:%S")),
        "labels": labels
    }
    print("ES payload:", payload)
    response = http.request('POST', url, headers=headers, body=json.dumps(payload))
    status = response.status
    data = json.loads(response.data)
    print("ES Response: [%s] %s" % (status, data))

def get_s3_metadata(bucket, file):
    """
    Get the object metadata from S3
    """
    print("Get custom labels for %s - %s" % (bucket, file))
    s3 = boto3.client("s3", region_name='us-east-1')
    response = s3.head_object(Bucket=bucket, Key=file)
    print("S3 head obj:", response)
    custom_labels = response["Metadata"].get("customlabels", "")
    custom_labels = list(filter(lambda x: x, map(lambda x: x.strip(), custom_labels.split(","))))
    print("Custom labels:", custom_labels)
    return custom_labels

def detect_img_labels(bucket, file):
    """
    Detect image labels using Rekognition
    """
    print("Detect labels for %s - %s" % (bucket, file))
    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': file}},
        MaxLabels=10,
        MinConfidence=95)
    print("Rekognition response:", response)
    labels = []
    for val in response['Labels']:
        labels.append(val['Name'])
    print("Detected labels:", labels)
    return labels

def lambda_handler(event, context):
    print("Event", event)

    records = event.get("Records", [])
    for record in records:
        bucket = record["s3"]["bucket"]["name"]
        file = record["s3"]["object"]["key"]
        labels = detect_img_labels(bucket, file)
        labels += get_s3_metadata(bucket, file)
        labels = list(set(map(lambda x: x.lower(), labels)))
        print("Labels for %s - %s: %s" % (bucket, file, labels))
        store_in_es(bucket, file, labels)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
