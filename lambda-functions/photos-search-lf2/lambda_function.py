import json
import boto3
import urllib3
import inflect

ES_CONFIG = {
    "url": "https://search-yelp-restaurants-es-coi3ozmqyi2g5vr624aing4dja.us-east-1.es.amazonaws.com/",
    "index": "photos",
    "type": "photo",
    "master-username": "chatbot-es-root",
    "master-password": "CCBD-es-123456"
}

lex_config = {
    "botName": 'PhotoSearchBot',
    "botAlias": 'test',
    'userId': 'ethibjsdj7b5fh2embctau00wo4yl2ws'
}


def search_es(search_labels):
    """
    Make an Elasticsearch query
    """
    http = urllib3.PoolManager()
    url = "%s%s/%s/_search?" % (ES_CONFIG["url"], ES_CONFIG["index"], ES_CONFIG["type"])
    headers = urllib3.make_headers(basic_auth='%s:%s' % (ES_CONFIG["master-username"], ES_CONFIG["master-password"]))
    headers.update({
        'Content-Type': 'application/json',
        "Accept": "application/json"
    })

    all_responses = []
    payload = {
        "query": {
            "terms": {
                "labels": search_labels
            }
        }
    }

    response = http.request('GET', url, headers=headers, body=json.dumps(payload))
    status = response.status
    data = json.loads(response.data)
    print("ES Response: [%s] %s" % (status, data))

    data = data['hits']['hits']
    for d in data:
        image_url = "https://" + d['_source']['bucket'] + ".s3.amazonaws.com/" + d['_source']['object_key']
        all_responses.append({
            'image-url': image_url,
            'labels': d['_source']['labels']
        })

    print("Image data: %s" % all_responses)
    return all_responses


def prepare_error_response():
    return []


def prepare_search_response(images_data):
    unique_images = list({x['image-url']: x for x in images_data}.values())
    print(unique_images)
    return unique_images


def lex_handler(msg):
    # LexV2 client uses 'lexv2-runtime'
    client = boto3.client('lex-runtime')
    p = inflect.engine()
    # Submit the text
    print('Lex request - config: %s, text: %s' % (lex_config, msg))
    lex_config['inputText'] = msg
    response = client.post_text(**lex_config)
    print('Lex response: %s' % response)
    slots = response['slots']
    keywords = []
    for k in slots.keys():
        if slots[k] != 'None':
            word = p.singular_noun(slots[k])
            if word == False:
                # Failed to convert to singular
                word = slots[k]
            keywords.append(word)

    print('keywords: ', keywords)
    return keywords


def lambda_handler(event, context):
    print("Event: %s" % event)

    try:
        query_text = event["q"]
        lex_response_labels = lex_handler(query_text)  # send query to lex and get labels
        images_data = search_es(lex_response_labels)
        response = prepare_search_response(images_data)
    except Exception as e:
        print("Error: %s" % str(e))
        response = prepare_error_response()

    print("Response: %s" % response)
    return response
